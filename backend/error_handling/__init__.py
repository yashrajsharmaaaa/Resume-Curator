"""
Error handling module for Resume Curator backend.

Provides comprehensive error handling with standardized responses,
error codes, logging, and user-friendly message translation.
"""

from .error_codes import ErrorCode, ErrorCategory
from .error_responses import (
    StandardErrorResponse, ErrorDetail, create_error_response,
    ValidationErrorResponse, SecurityErrorResponse, RateLimitErrorResponse
)
from .error_handlers import (
    register_error_handlers, handle_validation_error, handle_http_error,
    handle_generic_error, handle_security_error
)
from .error_logger import ErrorLogger, log_error, log_security_event
from .message_translator import MessageTranslator, translate_error_message, get_supported_languages

__all__ = [
    # Error codes
    'ErrorCode',
    'ErrorCategory',
    
    # Error responses
    'StandardErrorResponse',
    'ErrorDetail',
    'create_error_response',
    'ValidationErrorResponse',
    'SecurityErrorResponse', 
    'RateLimitErrorResponse',
    
    # Error handlers
    'register_error_handlers',
    'handle_validation_error',
    'handle_http_error',
    'handle_generic_error',
    'handle_security_error',
    
    # Error logging
    'ErrorLogger',
    'log_error',
    'log_security_event',
    
    # Message translation
    'MessageTranslator',
    'translate_error_message',
    'get_supported_languages'
]