"""
Standardized error response models for Resume Curator backend.

Provides consistent error response formats with detailed information
for different types of errors while maintaining security.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field

from .error_codes import ErrorCode, ErrorCategory, get_error_category, get_http_status_code


class ErrorDetail(BaseModel):
    """Detailed information about a specific error."""
    field: Optional[str] = Field(None, description="Field that caused the error")
    code: str = Field(..., description="Specific error code")
    message: str = Field(..., description="Human-readable error message")
    value: Optional[Any] = Field(None, description="Value that caused the error (sanitized)")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class StandardErrorResponse(BaseModel):
    """Standard error response format for all API errors."""
    
    # Core error information
    error: bool = Field(True, description="Always true for error responses")
    error_code: ErrorCode = Field(..., description="Standardized error code")
    error_category: ErrorCategory = Field(..., description="Error category")
    message: str = Field(..., description="User-friendly error message")
    
    # Additional details
    details: Optional[List[ErrorDetail]] = Field(None, description="Detailed error information")
    suggestions: Optional[List[str]] = Field(None, description="Suggestions for fixing the error")
    documentation_url: Optional[str] = Field(None, description="Link to relevant documentation")
    
    # Request tracking
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique request identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    # Rate limiting information (when applicable)
    retry_after: Optional[int] = Field(None, description="Seconds to wait before retrying")
    
    # Debug information (only in development)
    debug_info: Optional[Dict[str, Any]] = Field(None, description="Debug information (development only)")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ValidationErrorResponse(StandardErrorResponse):
    """Specialized error response for validation errors."""
    
    validation_errors: List[ErrorDetail] = Field(..., description="List of validation errors")
    invalid_fields: List[str] = Field(..., description="List of fields that failed validation")
    
    def __init__(self, **data):
        # Set default values for validation errors
        if 'error_code' not in data:
            data['error_code'] = ErrorCode.VALIDATION_FAILED
        if 'error_category' not in data:
            data['error_category'] = ErrorCategory.VALIDATION
        if 'message' not in data:
            data['message'] = "Request validation failed"
        
        super().__init__(**data)


class SecurityErrorResponse(StandardErrorResponse):
    """Specialized error response for security violations."""
    
    security_event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Security event ID")
    blocked_reason: str = Field(..., description="Reason for blocking the request")
    
    def __init__(self, **data):
        # Set default values for security errors
        if 'error_code' not in data:
            data['error_code'] = ErrorCode.SECURITY_VIOLATION
        if 'error_category' not in data:
            data['error_category'] = ErrorCategory.SECURITY
        if 'message' not in data:
            data['message'] = "Request blocked due to security violation"
        
        super().__init__(**data)


class RateLimitErrorResponse(StandardErrorResponse):
    """Specialized error response for rate limiting."""
    
    limit: int = Field(..., description="Request limit")
    remaining: int = Field(0, description="Remaining requests")
    reset_time: datetime = Field(..., description="When the limit resets")
    window_seconds: int = Field(..., description="Rate limit window in seconds")
    
    def __init__(self, **data):
        # Set default values for rate limit errors
        if 'error_code' not in data:
            data['error_code'] = ErrorCode.RATE_LIMIT_EXCEEDED
        if 'error_category' not in data:
            data['error_category'] = ErrorCategory.RATE_LIMITING
        if 'message' not in data:
            data['message'] = "Rate limit exceeded"
        
        super().__init__(**data)


class FileProcessingErrorResponse(StandardErrorResponse):
    """Specialized error response for file processing errors."""
    
    filename: Optional[str] = Field(None, description="Name of the file that caused the error")
    file_size: Optional[int] = Field(None, description="Size of the file in bytes")
    file_type: Optional[str] = Field(None, description="Detected file type")
    processing_stage: Optional[str] = Field(None, description="Stage where processing failed")
    
    def __init__(self, **data):
        # Set default values for file processing errors
        if 'error_code' not in data:
            data['error_code'] = ErrorCode.FILE_PROCESSING_FAILED
        if 'error_category' not in data:
            data['error_category'] = ErrorCategory.FILE_PROCESSING
        if 'message' not in data:
            data['message'] = "File processing failed"
        
        super().__init__(**data)


class AIAnalysisErrorResponse(StandardErrorResponse):
    """Specialized error response for AI analysis errors."""
    
    analysis_id: Optional[str] = Field(None, description="Analysis request ID")
    analysis_stage: Optional[str] = Field(None, description="Stage where analysis failed")
    model_used: Optional[str] = Field(None, description="AI model that was used")
    
    def __init__(self, **data):
        # Set default values for AI analysis errors
        if 'error_code' not in data:
            data['error_code'] = ErrorCode.AI_ANALYSIS_FAILED
        if 'error_category' not in data:
            data['error_category'] = ErrorCategory.AI_ANALYSIS
        if 'message' not in data:
            data['message'] = "AI analysis failed"
        
        super().__init__(**data)


def create_error_response(
    error_code: ErrorCode,
    message: Optional[str] = None,
    details: Optional[List[ErrorDetail]] = None,
    suggestions: Optional[List[str]] = None,
    debug_info: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
    **kwargs
) -> StandardErrorResponse:
    """
    Create a standardized error response.
    
    Args:
        error_code: The error code
        message: Custom error message (optional)
        details: Detailed error information
        suggestions: Suggestions for fixing the error
        debug_info: Debug information (development only)
        request_id: Custom request ID
        **kwargs: Additional fields for specialized error responses
        
    Returns:
        Appropriate error response object
    """
    category = get_error_category(error_code)
    
    # Use default message if none provided
    if message is None:
        message = get_default_error_message(error_code)
    
    # Base response data
    response_data = {
        'error_code': error_code,
        'error_category': category,
        'message': message,
        'details': details or [],
        'suggestions': suggestions or get_default_suggestions(error_code),
        'documentation_url': get_documentation_url(error_code),
        'debug_info': debug_info,
        **kwargs
    }
    
    if request_id:
        response_data['request_id'] = request_id
    
    # Create specialized response based on category
    if category == ErrorCategory.VALIDATION:
        # Extract validation-specific information
        validation_errors = []
        invalid_fields = []
        
        if details:
            for detail in details:
                if isinstance(detail, dict):
                    # Convert dict to ErrorDetail
                    error_detail = ErrorDetail(**detail)
                    validation_errors.append(error_detail)
                    if error_detail.field:
                        invalid_fields.append(error_detail.field)
                elif isinstance(detail, ErrorDetail):
                    validation_errors.append(detail)
                    if detail.field:
                        invalid_fields.append(detail.field)
        
        return ValidationErrorResponse(
            validation_errors=validation_errors,
            invalid_fields=invalid_fields,
            **response_data
        )
    
    elif category == ErrorCategory.SECURITY:
        blocked_reason = kwargs.pop('blocked_reason', 'Security policy violation')
        # Remove blocked_reason from response_data if it exists
        response_data.pop('blocked_reason', None)
        return SecurityErrorResponse(
            blocked_reason=blocked_reason,
            **response_data
        )
    
    elif category == ErrorCategory.RATE_LIMITING:
        # Rate limiting requires specific fields
        required_fields = ['limit', 'remaining', 'reset_time', 'window_seconds']
        if all(field in kwargs for field in required_fields):
            return RateLimitErrorResponse(**response_data)
    
    elif category == ErrorCategory.FILE_PROCESSING:
        return FileProcessingErrorResponse(**response_data)
    
    elif category == ErrorCategory.AI_ANALYSIS:
        return AIAnalysisErrorResponse(**response_data)
    
    # Default to standard error response
    return StandardErrorResponse(**response_data)


def get_default_error_message(error_code: ErrorCode) -> str:
    """
    Get the default user-friendly message for an error code.
    
    Args:
        error_code: The error code
        
    Returns:
        User-friendly error message
    """
    messages = {
        # Validation errors
        ErrorCode.VALIDATION_FAILED: "The request contains invalid data. Please check your input and try again.",
        ErrorCode.INVALID_INPUT_FORMAT: "The input format is invalid. Please check the required format.",
        ErrorCode.MISSING_REQUIRED_FIELD: "A required field is missing. Please provide all required information.",
        ErrorCode.FIELD_TOO_SHORT: "One or more fields are too short. Please provide more detailed information.",
        ErrorCode.FIELD_TOO_LONG: "One or more fields exceed the maximum length. Please shorten your input.",
        ErrorCode.INVALID_EMAIL_FORMAT: "The email address format is invalid.",
        ErrorCode.INVALID_PHONE_FORMAT: "The phone number format is invalid.",
        ErrorCode.INVALID_DATE_FORMAT: "The date format is invalid. Please use the correct format.",
        ErrorCode.INVALID_JSON_FORMAT: "The request contains invalid JSON. Please check the format.",
        ErrorCode.INVALID_CONTENT_TYPE: "The content type is not supported for this endpoint.",
        
        # File processing errors
        ErrorCode.FILE_NOT_PROVIDED: "No file was provided. Please select a file to upload.",
        ErrorCode.FILE_TOO_LARGE: "The file is too large. Please use a file smaller than the maximum size limit.",
        ErrorCode.FILE_TOO_SMALL: "The file is too small or empty. Please provide a valid file.",
        ErrorCode.INVALID_FILE_TYPE: "The file type is not supported. Please use a PDF, DOC, or DOCX file.",
        ErrorCode.FILE_CORRUPTED: "The file appears to be corrupted. Please try uploading a different file.",
        ErrorCode.FILE_PROCESSING_FAILED: "We couldn't process your file. Please try again or use a different file.",
        ErrorCode.FILE_UPLOAD_FAILED: "File upload failed. Please check your connection and try again.",
        ErrorCode.FILE_NOT_FOUND: "The requested file was not found.",
        ErrorCode.UNSUPPORTED_FILE_FORMAT: "This file format is not supported. Please use PDF, DOC, or DOCX.",
        
        # AI analysis errors
        ErrorCode.AI_SERVICE_UNAVAILABLE: "The AI analysis service is temporarily unavailable. Please try again later.",
        ErrorCode.AI_ANALYSIS_FAILED: "The analysis could not be completed. Please try again.",
        ErrorCode.AI_QUOTA_EXCEEDED: "The AI service quota has been exceeded. Please try again later.",
        ErrorCode.AI_TIMEOUT: "The analysis took too long to complete. Please try again.",
        ErrorCode.INVALID_ANALYSIS_REQUEST: "The analysis request is invalid. Please check your input.",
        ErrorCode.ANALYSIS_IN_PROGRESS: "An analysis is already in progress. Please wait for it to complete.",
        ErrorCode.ANALYSIS_NOT_FOUND: "The requested analysis was not found.",
        ErrorCode.INSUFFICIENT_CONTENT: "There isn't enough content to perform a meaningful analysis.",
        ErrorCode.ANALYSIS_EXPIRED: "The analysis results have expired. Please start a new analysis.",
        
        # Rate limiting errors
        ErrorCode.RATE_LIMIT_EXCEEDED: "You've made too many requests. Please wait before trying again.",
        ErrorCode.TOO_MANY_REQUESTS: "Too many requests in a short time. Please slow down.",
        ErrorCode.QUOTA_EXCEEDED: "Your usage quota has been exceeded. Please try again later.",
        ErrorCode.REQUEST_BLOCKED: "Your request has been blocked. Please contact support if this continues.",
        ErrorCode.CLIENT_BANNED: "Your access has been temporarily restricted. Please contact support.",
        
        # Security errors
        ErrorCode.SECURITY_VIOLATION: "Your request was blocked for security reasons.",
        ErrorCode.SUSPICIOUS_ACTIVITY: "Suspicious activity detected. Your request has been blocked.",
        ErrorCode.MALICIOUS_CONTENT_DETECTED: "Potentially malicious content was detected in your request.",
        ErrorCode.XSS_ATTEMPT_BLOCKED: "Your request was blocked due to potential security risks.",
        ErrorCode.UNSAFE_FILE_DETECTED: "The uploaded file was flagged as potentially unsafe.",
        ErrorCode.IP_BLOCKED: "Your IP address has been temporarily blocked.",
        
        # Database errors
        ErrorCode.DATABASE_CONNECTION_FAILED: "We're experiencing database connectivity issues. Please try again.",
        ErrorCode.DATABASE_QUERY_FAILED: "A database error occurred. Please try again.",
        ErrorCode.RECORD_NOT_FOUND: "The requested record was not found.",
        ErrorCode.DUPLICATE_RECORD: "A record with this information already exists.",
        ErrorCode.DATABASE_TIMEOUT: "The database operation timed out. Please try again.",
        ErrorCode.DATABASE_UNAVAILABLE: "The database is temporarily unavailable. Please try again later.",
        
        # System errors
        ErrorCode.INTERNAL_SERVER_ERROR: "An internal server error occurred. Please try again.",
        ErrorCode.SERVICE_TEMPORARILY_UNAVAILABLE: "The service is temporarily unavailable. Please try again later.",
        ErrorCode.CONFIGURATION_ERROR: "A configuration error occurred. Please contact support.",
        ErrorCode.RESOURCE_EXHAUSTED: "System resources are temporarily exhausted. Please try again later.",
        ErrorCode.MAINTENANCE_MODE: "The system is currently under maintenance. Please try again later.",
        
        # Business logic errors
        ErrorCode.RESUME_SESSION_EXPIRED: "Your resume session has expired. Please upload your resume again.",
        ErrorCode.ANALYSIS_ALREADY_EXISTS: "An analysis for this combination already exists.",
        ErrorCode.INVALID_OPERATION_STATE: "This operation cannot be performed in the current state.",
        ErrorCode.BUSINESS_RULE_VIOLATION: "This operation violates business rules.",
    }
    
    return messages.get(error_code, "An error occurred. Please try again.")


def get_default_suggestions(error_code: ErrorCode) -> List[str]:
    """
    Get default suggestions for fixing an error.
    
    Args:
        error_code: The error code
        
    Returns:
        List of suggestions
    """
    suggestions = {
        ErrorCode.FILE_TOO_LARGE: [
            "Compress your file to reduce its size",
            "Use a PDF instead of a Word document for smaller file size",
            "Remove unnecessary images or formatting from your resume"
        ],
        ErrorCode.INVALID_FILE_TYPE: [
            "Convert your file to PDF, DOC, or DOCX format",
            "Make sure your file has the correct extension (.pdf, .doc, .docx)"
        ],
        ErrorCode.FIELD_TOO_SHORT: [
            "Provide more detailed information in the required fields",
            "Make sure your job description includes responsibilities and requirements"
        ],
        ErrorCode.RATE_LIMIT_EXCEEDED: [
            "Wait a few minutes before making another request",
            "Reduce the frequency of your requests"
        ],
        ErrorCode.AI_SERVICE_UNAVAILABLE: [
            "Try again in a few minutes",
            "Check our status page for service updates"
        ],
        ErrorCode.INSUFFICIENT_CONTENT: [
            "Provide a more detailed resume with work experience and skills",
            "Include a comprehensive job description with requirements"
        ]
    }
    
    return suggestions.get(error_code, ["Please try again", "Contact support if the problem persists"])


def get_documentation_url(error_code: ErrorCode) -> Optional[str]:
    """
    Get documentation URL for an error code.
    
    Args:
        error_code: The error code
        
    Returns:
        Documentation URL or None
    """
    base_url = "https://docs.resumecurator.com/errors"
    
    # Map error categories to documentation sections
    category = get_error_category(error_code)
    category_urls = {
        ErrorCategory.VALIDATION: f"{base_url}/validation",
        ErrorCategory.FILE_PROCESSING: f"{base_url}/file-processing",
        ErrorCategory.AI_ANALYSIS: f"{base_url}/ai-analysis",
        ErrorCategory.RATE_LIMITING: f"{base_url}/rate-limiting",
        ErrorCategory.SECURITY: f"{base_url}/security",
    }
    
    return category_urls.get(category)


def sanitize_error_value(value: Any) -> Any:
    """
    Sanitize error values to prevent information leakage.
    
    Args:
        value: The value to sanitize
        
    Returns:
        Sanitized value
    """
    if value is None:
        return None
    
    # Convert to string and limit length
    str_value = str(value)
    if len(str_value) > 100:
        return str_value[:97] + "..."
    
    # Remove potentially sensitive patterns
    import re
    
    # Remove email addresses
    str_value = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', str_value)
    
    # Remove phone numbers
    str_value = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', str_value)
    
    # Remove potential passwords or tokens
    str_value = re.sub(r'\b[A-Za-z0-9]{20,}\b', '[TOKEN]', str_value)
    
    return str_value