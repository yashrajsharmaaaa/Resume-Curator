"""
Input validation and security for Resume Curator application.

This module provides essential validation and security features:
- File type and size validation
- Input sanitization
- Basic rate limiting
- MIME type verification

Designed for SDE1 portfolio demonstration with clean, focused implementation.
"""

import re
import html
import time
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
from datetime import datetime, timedelta

from fastapi import UploadFile, HTTPException, Request, status
from pydantic import BaseModel

# Try to import magic, but handle if not available
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    magic = None


# Configuration constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx'}
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
}

# Rate limiting configuration
RATE_LIMITS = {
    'upload': {'requests': 10, 'window': 60},      # 10 uploads per minute
    'analysis': {'requests': 5, 'window': 300},    # 5 analyses per 5 minutes
    'health': {'requests': 120, 'window': 60},     # 120 health checks per minute
    'default': {'requests': 60, 'window': 60},     # 60 requests per minute
}


class ValidationError(BaseModel):
    """Standard validation error model."""
    field: str
    message: str
    code: str


class ValidationResult(BaseModel):
    """Validation result with errors and warnings."""
    is_valid: bool = True
    errors: List[ValidationError] = []
    warnings: List[ValidationError] = []
    metadata: Dict[str, Any] = {}


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self.clients: Dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, client_id: str, endpoint_type: str = 'default') -> bool:
        """Check if request is allowed under rate limits."""
        config = RATE_LIMITS.get(endpoint_type, RATE_LIMITS['default'])
        now = time.time()
        window = config['window']
        limit = config['requests']
        
        # Clean old requests
        client_requests = self.clients[client_id]
        while client_requests and client_requests[0] <= now - window:
            client_requests.popleft()
        
        # Check limit
        if len(client_requests) >= limit:
            return False
        
        # Record request
        client_requests.append(now)
        return True
    
    def get_retry_after(self, client_id: str, endpoint_type: str = 'default') -> int:
        """Get retry-after time in seconds."""
        config = RATE_LIMITS.get(endpoint_type, RATE_LIMITS['default'])
        client_requests = self.clients[client_id]
        
        if not client_requests:
            return 0
        
        oldest_request = client_requests[0]
        return max(0, int(oldest_request + config['window'] - time.time()))


# Global rate limiter instance
rate_limiter = RateLimiter()


def get_client_id(request: Request) -> str:
    """Get client identifier from request."""
    return request.client.host if request.client else "unknown"


def check_rate_limit(request: Request, endpoint_type: str = 'default') -> None:
    """Check rate limit and raise HTTPException if exceeded."""
    client_id = get_client_id(request)
    
    if not rate_limiter.is_allowed(client_id, endpoint_type):
        retry_after = rate_limiter.get_retry_after(client_id, endpoint_type)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": f"Rate limit exceeded for {endpoint_type}",
                    "retry_after": retry_after
                }
            },
            headers={"Retry-After": str(retry_after)}
        )


def validate_file_upload(file: UploadFile) -> ValidationResult:
    """
    Validate uploaded resume file.
    
    Checks:
    - File presence and name
    - File size limits
    - File extension
    - MIME type
    - Basic content validation
    
    Args:
        file: Uploaded file to validate
        
    Returns:
        ValidationResult with validation status and details
    """
    result = ValidationResult()
    
    # Check file presence
    if not file or not file.filename:
        result.errors.append(ValidationError(
            field="file",
            message="No file provided",
            code="FILE_REQUIRED"
        ))
        result.is_valid = False
        return result
    
    # Check file extension
    file_ext = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    if file_ext not in ALLOWED_EXTENSIONS:
        result.errors.append(ValidationError(
            field="file",
            message=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
            code="INVALID_FILE_TYPE"
        ))
        result.is_valid = False
        return result
    
    # Read file content for size and content validation
    try:
        file_content = file.file.read()
        file.file.seek(0)  # Reset file pointer
    except Exception as e:
        result.errors.append(ValidationError(
            field="file",
            message=f"Could not read file: {str(e)}",
            code="FILE_READ_ERROR"
        ))
        result.is_valid = False
        return result
    
    # Check file size
    file_size = len(file_content)
    if file_size == 0:
        result.errors.append(ValidationError(
            field="file",
            message="File is empty",
            code="FILE_EMPTY"
        ))
        result.is_valid = False
        return result
    
    if file_size > MAX_FILE_SIZE:
        result.errors.append(ValidationError(
            field="file",
            message=f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds limit ({MAX_FILE_SIZE / 1024 / 1024}MB)",
            code="FILE_TOO_LARGE"
        ))
        result.is_valid = False
        return result
    
    # Check MIME type
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        result.warnings.append(ValidationError(
            field="content_type",
            message=f"Unexpected MIME type: {file.content_type}",
            code="UNEXPECTED_MIME_TYPE"
        ))
    
    # Basic content validation
    if file_ext == '.pdf' and not file_content.startswith(b'%PDF-'):
        result.errors.append(ValidationError(
            field="file",
            message="File does not appear to be a valid PDF",
            code="INVALID_PDF"
        ))
        result.is_valid = False
    elif file_ext == '.docx' and not file_content.startswith(b'PK'):
        result.errors.append(ValidationError(
            field="file",
            message="File does not appear to be a valid DOCX document",
            code="INVALID_DOCX"
        ))
        result.is_valid = False
    
    # Security check for suspicious content
    suspicious_patterns = [b'<script', b'javascript:', b'vbscript:', b'<?php']
    for pattern in suspicious_patterns:
        if pattern in file_content.lower():
            result.errors.append(ValidationError(
                field="file",
                message="File contains potentially malicious content",
                code="SECURITY_VIOLATION"
            ))
            result.is_valid = False
            break
    
    # Add metadata
    result.metadata = {
        'filename': sanitize_filename(file.filename),
        'file_size': file_size,
        'content_type': file.content_type,
        'file_extension': file_ext
    }
    
    return result


def validate_job_description(job_description: str) -> ValidationResult:
    """
    Validate job description input.
    
    Args:
        job_description: Job description text to validate
        
    Returns:
        ValidationResult with validation status and details
    """
    result = ValidationResult()
    
    if not job_description or not job_description.strip():
        result.errors.append(ValidationError(
            field="job_description",
            message="Job description is required",
            code="REQUIRED"
        ))
        result.is_valid = False
        return result
    
    # Sanitize and validate length
    sanitized = sanitize_text_input(job_description)
    word_count = len(sanitized.split())
    
    if len(sanitized) < 10:
        result.errors.append(ValidationError(
            field="job_description",
            message="Job description is too short (minimum 10 characters)",
            code="TOO_SHORT"
        ))
        result.is_valid = False
    elif len(sanitized) > 10000:
        result.errors.append(ValidationError(
            field="job_description",
            message="Job description is too long (maximum 10,000 characters)",
            code="TOO_LONG"
        ))
        result.is_valid = False
    
    # Quality warnings
    if word_count < 20:
        result.warnings.append(ValidationError(
            field="job_description",
            message="Job description is quite short. More details may improve analysis quality.",
            code="SHORT_DESCRIPTION"
        ))
    
    result.metadata = {
        'original_length': len(job_description),
        'sanitized_length': len(sanitized),
        'word_count': word_count,
        'sanitized_content': sanitized
    }
    
    return result


def sanitize_text_input(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize text input to prevent XSS and other security issues.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # HTML escape to prevent XSS
    sanitized = html.escape(text, quote=False)
    
    # Remove potentially dangerous patterns
    dangerous_patterns = [
        r'javascript:',
        r'vbscript:',
        r'data:',
        r'on\w+\s*=',
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
    ]
    
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    
    # Normalize whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    # Truncate if necessary
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip()
    
    return sanitized


def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize text input - alias for sanitize_text_input for frontend compatibility.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    return sanitize_text_input(text, max_length)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and other issues.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return "unnamed_file"
    
    # Remove path components
    filename = filename.split('/')[-1].split('\\')[-1]
    
    # Remove dangerous characters
    filename = re.sub(r'[<>:"|?*]', '', filename)
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        max_name_length = 255 - len(ext) - 1 if ext else 255
        filename = name[:max_name_length] + ('.' + ext if ext else '')
    
    return filename


def create_validation_error(
    error_code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 400
) -> HTTPException:
    """
    Create a standardized HTTP validation error.
    
    Args:
        error_code: Error code
        message: Error message
        details: Additional error details
        status_code: HTTP status code
        
    Returns:
        HTTPException with standardized error format
    """
    return HTTPException(
        status_code=status_code,
        detail={
            "error": {
                "code": error_code,
                "message": message,
                "details": details or {}
            }
        }
    )


def validate_and_raise(validation_result: ValidationResult, field_name: str = "input") -> None:
    """
    Check validation result and raise HTTPException if invalid.
    
    Args:
        validation_result: Validation result to check
        field_name: Name of the field being validated
        
    Raises:
        HTTPException: If validation failed
    """
    if not validation_result.is_valid:
        error_messages = [error.message for error in validation_result.errors]
        raise create_validation_error(
            error_code="VALIDATION_ERROR",
            message=f"Validation failed for {field_name}: {'; '.join(error_messages)}",
            details={
                "errors": [error.dict() for error in validation_result.errors],
                "warnings": [warning.dict() for warning in validation_result.warnings],
                "metadata": validation_result.metadata
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )