"""
Error handlers for Resume Curator backend.

Provides centralized error handling with proper logging,
response formatting, and security considerations.
"""

import logging
import traceback
from typing import Dict, Any, Optional, Union
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError

from .error_codes import ErrorCode, get_http_status_code, should_log_error
from .error_responses import (
    StandardErrorResponse, ValidationErrorResponse, SecurityErrorResponse,
    ErrorDetail, create_error_response, sanitize_error_value
)
from .error_logger import log_error, log_security_event
from .message_translator import translate_error_message

logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    """
    Register all error handlers with the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """Handle HTTP exceptions."""
        return await handle_http_error(request, exc)
    
    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """Handle Starlette HTTP exceptions."""
        return await handle_http_error(request, exc)
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle request validation errors."""
        return await handle_validation_error(request, exc)
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
        """Handle Pydantic validation errors."""
        return await handle_validation_error(request, exc)
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle all other exceptions."""
        return await handle_generic_error(request, exc)


async def handle_http_error(
    request: Request, 
    exc: Union[HTTPException, StarletteHTTPException]
) -> JSONResponse:
    """
    Handle HTTP exceptions with proper error response formatting.
    
    Args:
        request: The HTTP request
        exc: The HTTP exception
        
    Returns:
        JSON error response
    """
    try:
        # Determine error code based on status code and detail
        error_code = _map_http_status_to_error_code(exc.status_code, str(exc.detail))
        
        # Extract additional information from exception
        details = []
        if hasattr(exc, 'detail') and isinstance(exc.detail, dict):
            # Handle structured error details
            if 'errors' in exc.detail:
                for error in exc.detail['errors']:
                    details.append(ErrorDetail(
                        field=error.get('field'),
                        code=error.get('code', error_code.value),
                        message=error.get('message', str(exc.detail)),
                        value=sanitize_error_value(error.get('value'))
                    ))
        
        # Create error response
        error_response = create_error_response(
            error_code=error_code,
            message=_extract_user_friendly_message(exc.detail),
            details=details if details else None,
            request_id=_get_request_id(request)
        )
        
        # Log error if necessary
        if should_log_error(error_code):
            await log_error(
                error_code=error_code,
                message=str(exc.detail),
                request=request,
                exception=exc,
                additional_data={
                    'status_code': exc.status_code,
                    'request_id': error_response.request_id
                }
            )
        
        # Translate message if needed
        translated_message = await translate_error_message(
            error_response.message,
            _get_client_language(request)
        )
        if translated_message != error_response.message:
            error_response.message = translated_message
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.dict(),
            headers=_get_error_headers(error_response)
        )
        
    except Exception as handler_error:
        logger.error(f"Error in HTTP exception handler: {handler_error}")
        return _create_fallback_error_response(exc.status_code)


async def handle_validation_error(
    request: Request,
    exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:
    """
    Handle validation errors with detailed field information.
    
    Args:
        request: The HTTP request
        exc: The validation exception
        
    Returns:
        JSON error response
    """
    try:
        # Extract validation errors
        validation_errors = []
        invalid_fields = []
        
        if isinstance(exc, RequestValidationError):
            for error in exc.errors():
                field_name = '.'.join(str(loc) for loc in error['loc']) if error['loc'] else 'request'
                invalid_fields.append(field_name)
                
                validation_errors.append(ErrorDetail(
                    field=field_name,
                    code=f"validation_{error['type']}",
                    message=error['msg'],
                    value=sanitize_error_value(error.get('input')),
                    context={'type': error['type']}
                ))
        
        elif isinstance(exc, ValidationError):
            for error in exc.errors():
                field_name = '.'.join(str(loc) for loc in error['loc']) if error['loc'] else 'field'
                invalid_fields.append(field_name)
                
                validation_errors.append(ErrorDetail(
                    field=field_name,
                    code=f"validation_{error['type']}",
                    message=error['msg'],
                    value=sanitize_error_value(error.get('input')),
                    context={'type': error['type']}
                ))
        
        # Create validation error response
        error_response = ValidationErrorResponse(
            validation_errors=validation_errors,
            invalid_fields=list(set(invalid_fields)),  # Remove duplicates
            details=validation_errors,
            request_id=_get_request_id(request)
        )
        
        # Log validation error
        await log_error(
            error_code=ErrorCode.VALIDATION_FAILED,
            message=f"Validation failed for {len(invalid_fields)} fields",
            request=request,
            exception=exc,
            additional_data={
                'invalid_fields': invalid_fields,
                'validation_error_count': len(validation_errors),
                'request_id': error_response.request_id
            }
        )
        
        # Translate message if needed
        translated_message = await translate_error_message(
            error_response.message,
            _get_client_language(request)
        )
        if translated_message != error_response.message:
            error_response.message = translated_message
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.dict(),
            headers=_get_error_headers(error_response)
        )
        
    except Exception as handler_error:
        logger.error(f"Error in validation exception handler: {handler_error}")
        return _create_fallback_error_response(status.HTTP_422_UNPROCESSABLE_ENTITY)


async def handle_security_error(
    request: Request,
    error_code: ErrorCode,
    message: str,
    blocked_reason: str,
    additional_data: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Handle security-related errors with proper logging and response.
    
    Args:
        request: The HTTP request
        error_code: Security error code
        message: Error message
        blocked_reason: Reason for blocking
        additional_data: Additional data for logging
        
    Returns:
        JSON error response
    """
    try:
        # Create security error response
        error_response = SecurityErrorResponse(
            error_code=error_code,
            message=message,
            blocked_reason=blocked_reason,
            request_id=_get_request_id(request)
        )
        
        # Log security event
        await log_security_event(
            event_type=error_code.value,
            message=message,
            request=request,
            severity='high',
            additional_data={
                'blocked_reason': blocked_reason,
                'security_event_id': error_response.security_event_id,
                'request_id': error_response.request_id,
                **(additional_data or {})
            }
        )
        
        # Don't translate security messages to avoid information leakage
        
        return JSONResponse(
            status_code=get_http_status_code(error_code),
            content=error_response.dict(),
            headers=_get_error_headers(error_response)
        )
        
    except Exception as handler_error:
        logger.error(f"Error in security exception handler: {handler_error}")
        return _create_fallback_error_response(status.HTTP_400_BAD_REQUEST)


async def handle_generic_error(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle generic exceptions with proper logging and safe error responses.
    
    Args:
        request: The HTTP request
        exc: The exception
        
    Returns:
        JSON error response
    """
    try:
        # Determine error code based on exception type
        error_code = _map_exception_to_error_code(exc)
        
        # Create safe error message (don't expose internal details)
        safe_message = _create_safe_error_message(exc, error_code)
        
        # Create error response
        error_response = create_error_response(
            error_code=error_code,
            message=safe_message,
            request_id=_get_request_id(request)
        )
        
        # Log the full error with stack trace
        await log_error(
            error_code=error_code,
            message=str(exc),
            request=request,
            exception=exc,
            additional_data={
                'exception_type': type(exc).__name__,
                'stack_trace': traceback.format_exc(),
                'request_id': error_response.request_id
            }
        )
        
        # Translate message if needed
        translated_message = await translate_error_message(
            error_response.message,
            _get_client_language(request)
        )
        if translated_message != error_response.message:
            error_response.message = translated_message
        
        return JSONResponse(
            status_code=get_http_status_code(error_code),
            content=error_response.dict(),
            headers=_get_error_headers(error_response)
        )
        
    except Exception as handler_error:
        logger.error(f"Error in generic exception handler: {handler_error}")
        return _create_fallback_error_response(status.HTTP_500_INTERNAL_SERVER_ERROR)


def _map_http_status_to_error_code(status_code: int, detail: str) -> ErrorCode:
    """Map HTTP status code to error code."""
    # Check detail for specific error indicators
    detail_lower = detail.lower()
    
    if status_code == 400:
        if 'file' in detail_lower:
            if 'large' in detail_lower or 'size' in detail_lower:
                return ErrorCode.FILE_TOO_LARGE
            elif 'type' in detail_lower or 'format' in detail_lower:
                return ErrorCode.INVALID_FILE_TYPE
            else:
                return ErrorCode.FILE_PROCESSING_FAILED
        elif 'validation' in detail_lower:
            return ErrorCode.VALIDATION_FAILED
        elif 'json' in detail_lower:
            return ErrorCode.INVALID_JSON_FORMAT
        else:
            return ErrorCode.INVALID_INPUT_FORMAT
    
    elif status_code == 401:
        return ErrorCode.AUTHENTICATION_REQUIRED
    elif status_code == 403:
        return ErrorCode.INSUFFICIENT_PERMISSIONS
    elif status_code == 404:
        if 'file' in detail_lower:
            return ErrorCode.FILE_NOT_FOUND
        elif 'analysis' in detail_lower:
            return ErrorCode.ANALYSIS_NOT_FOUND
        else:
            return ErrorCode.RECORD_NOT_FOUND
    elif status_code == 413:
        return ErrorCode.FILE_TOO_LARGE
    elif status_code == 415:
        return ErrorCode.INVALID_CONTENT_TYPE
    elif status_code == 422:
        return ErrorCode.VALIDATION_FAILED
    elif status_code == 429:
        return ErrorCode.RATE_LIMIT_EXCEEDED
    elif status_code == 503:
        if 'ai' in detail_lower or 'analysis' in detail_lower:
            return ErrorCode.AI_SERVICE_UNAVAILABLE
        else:
            return ErrorCode.SERVICE_TEMPORARILY_UNAVAILABLE
    else:
        return ErrorCode.INTERNAL_SERVER_ERROR


def _map_exception_to_error_code(exc: Exception) -> ErrorCode:
    """Map exception type to error code."""
    exception_mapping = {
        'ConnectionError': ErrorCode.DATABASE_CONNECTION_FAILED,
        'TimeoutError': ErrorCode.DATABASE_TIMEOUT,
        'FileNotFoundError': ErrorCode.FILE_NOT_FOUND,
        'PermissionError': ErrorCode.FILE_PERMISSION_DENIED,
        'MemoryError': ErrorCode.MEMORY_LIMIT_EXCEEDED,
        'OSError': ErrorCode.SYSTEM,
        'ValueError': ErrorCode.INVALID_INPUT_FORMAT,
        'TypeError': ErrorCode.INVALID_INPUT_FORMAT,
        'KeyError': ErrorCode.MISSING_REQUIRED_FIELD,
    }
    
    exception_name = type(exc).__name__
    return exception_mapping.get(exception_name, ErrorCode.INTERNAL_SERVER_ERROR)


def _extract_user_friendly_message(detail: Any) -> str:
    """Extract user-friendly message from exception detail."""
    if isinstance(detail, str):
        return detail
    elif isinstance(detail, dict):
        return detail.get('message', 'An error occurred')
    else:
        return str(detail)


def _create_safe_error_message(exc: Exception, error_code: ErrorCode) -> str:
    """Create a safe error message that doesn't expose internal details."""
    # For certain exception types, we can be more specific
    if isinstance(exc, FileNotFoundError):
        return "The requested file was not found."
    elif isinstance(exc, PermissionError):
        return "Permission denied while accessing the resource."
    elif isinstance(exc, ValueError):
        return "Invalid input provided. Please check your data and try again."
    elif isinstance(exc, ConnectionError):
        return "Unable to connect to the service. Please try again later."
    elif isinstance(exc, TimeoutError):
        return "The operation timed out. Please try again."
    else:
        # Use the default message for the error code
        from .error_responses import get_default_error_message
        return get_default_error_message(error_code)


def _get_request_id(request: Request) -> str:
    """Get or generate request ID."""
    # Try to get existing request ID from headers
    request_id = request.headers.get('x-request-id')
    if not request_id:
        # Generate new request ID
        import uuid
        request_id = str(uuid.uuid4())
    return request_id


def _get_client_language(request: Request) -> str:
    """Get client language preference."""
    # Try to get language from Accept-Language header
    accept_language = request.headers.get('accept-language', 'en')
    # Extract primary language (e.g., 'en-US' -> 'en')
    return accept_language.split(',')[0].split('-')[0].lower()


def _get_error_headers(error_response: StandardErrorResponse) -> Dict[str, str]:
    """Get headers to include with error response."""
    headers = {
        'X-Request-ID': error_response.request_id,
        'X-Error-Code': error_response.error_code.value,
        'X-Error-Category': error_response.error_category.value,
        'Content-Type': 'application/json'
    }
    
    # Add retry-after header for rate limiting errors
    if error_response.retry_after:
        headers['Retry-After'] = str(error_response.retry_after)
    
    # Add security headers
    headers.update({
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block'
    })
    
    return headers


def _create_fallback_error_response(status_code: int) -> JSONResponse:
    """Create a fallback error response when error handling fails."""
    return JSONResponse(
        status_code=status_code,
        content={
            'error': True,
            'error_code': 'E9000',
            'error_category': 'system',
            'message': 'An internal error occurred',
            'timestamp': datetime.utcnow().isoformat(),
            'request_id': 'unknown'
        },
        headers={
            'Content-Type': 'application/json',
            'X-Content-Type-Options': 'nosniff'
        }
    )