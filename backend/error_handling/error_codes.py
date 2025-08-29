"""
Error codes and categories for Resume Curator backend.

Provides standardized error codes for consistent error handling
and user-friendly error messages across the application.
"""

from enum import Enum
from typing import Dict, Optional


class ErrorCategory(str, Enum):
    """Categories of errors for grouping and handling."""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RATE_LIMITING = "rate_limiting"
    FILE_PROCESSING = "file_processing"
    AI_ANALYSIS = "ai_analysis"
    DATABASE = "database"
    NETWORK = "network"
    SECURITY = "security"
    SYSTEM = "system"
    BUSINESS_LOGIC = "business_logic"


class ErrorCode(str, Enum):
    """Standardized error codes for the Resume Curator application."""
    
    # Validation Errors (1000-1999)
    VALIDATION_FAILED = "E1000"
    INVALID_INPUT_FORMAT = "E1001"
    MISSING_REQUIRED_FIELD = "E1002"
    FIELD_TOO_SHORT = "E1003"
    FIELD_TOO_LONG = "E1004"
    INVALID_EMAIL_FORMAT = "E1005"
    INVALID_PHONE_FORMAT = "E1006"
    INVALID_DATE_FORMAT = "E1007"
    INVALID_JSON_FORMAT = "E1008"
    INVALID_CONTENT_TYPE = "E1009"
    
    # File Processing Errors (2000-2999)
    FILE_NOT_PROVIDED = "E2000"
    FILE_TOO_LARGE = "E2001"
    FILE_TOO_SMALL = "E2002"
    INVALID_FILE_TYPE = "E2003"
    FILE_CORRUPTED = "E2004"
    FILE_PROCESSING_FAILED = "E2005"
    FILE_UPLOAD_FAILED = "E2006"
    FILE_NOT_FOUND = "E2007"
    FILE_PERMISSION_DENIED = "E2008"
    UNSUPPORTED_FILE_FORMAT = "E2009"
    
    # AI Analysis Errors (3000-3999)
    AI_SERVICE_UNAVAILABLE = "E3000"
    AI_ANALYSIS_FAILED = "E3001"
    AI_QUOTA_EXCEEDED = "E3002"
    AI_TIMEOUT = "E3003"
    INVALID_ANALYSIS_REQUEST = "E3004"
    ANALYSIS_IN_PROGRESS = "E3005"
    ANALYSIS_NOT_FOUND = "E3006"
    INSUFFICIENT_CONTENT = "E3007"
    AI_MODEL_ERROR = "E3008"
    ANALYSIS_EXPIRED = "E3009"
    
    # Rate Limiting Errors (4000-4999)
    RATE_LIMIT_EXCEEDED = "E4000"
    TOO_MANY_REQUESTS = "E4001"
    QUOTA_EXCEEDED = "E4002"
    REQUEST_BLOCKED = "E4003"
    CLIENT_BANNED = "E4004"
    CONCURRENT_LIMIT_EXCEEDED = "E4005"
    
    # Authentication & Authorization Errors (5000-5999)
    AUTHENTICATION_REQUIRED = "E5000"
    INVALID_CREDENTIALS = "E5001"
    TOKEN_EXPIRED = "E5002"
    TOKEN_INVALID = "E5003"
    INSUFFICIENT_PERMISSIONS = "E5004"
    ACCOUNT_DISABLED = "E5005"
    SESSION_EXPIRED = "E5006"
    
    # Security Errors (6000-6999)
    SECURITY_VIOLATION = "E6000"
    SUSPICIOUS_ACTIVITY = "E6001"
    MALICIOUS_CONTENT_DETECTED = "E6002"
    XSS_ATTEMPT_BLOCKED = "E6003"
    SQL_INJECTION_BLOCKED = "E6004"
    UNSAFE_FILE_DETECTED = "E6005"
    IP_BLOCKED = "E6006"
    CSRF_TOKEN_INVALID = "E6007"
    
    # Database Errors (7000-7999)
    DATABASE_CONNECTION_FAILED = "E7000"
    DATABASE_QUERY_FAILED = "E7001"
    RECORD_NOT_FOUND = "E7002"
    DUPLICATE_RECORD = "E7003"
    DATABASE_TIMEOUT = "E7004"
    TRANSACTION_FAILED = "E7005"
    CONSTRAINT_VIOLATION = "E7006"
    DATABASE_UNAVAILABLE = "E7007"
    
    # Network Errors (8000-8999)
    NETWORK_TIMEOUT = "E8000"
    CONNECTION_FAILED = "E8001"
    SERVICE_UNAVAILABLE = "E8002"
    EXTERNAL_API_ERROR = "E8003"
    DNS_RESOLUTION_FAILED = "E8004"
    SSL_CERTIFICATE_ERROR = "E8005"
    
    # System Errors (9000-9999)
    INTERNAL_SERVER_ERROR = "E9000"
    SERVICE_TEMPORARILY_UNAVAILABLE = "E9001"
    CONFIGURATION_ERROR = "E9002"
    RESOURCE_EXHAUSTED = "E9003"
    DISK_SPACE_FULL = "E9004"
    MEMORY_LIMIT_EXCEEDED = "E9005"
    CPU_LIMIT_EXCEEDED = "E9006"
    MAINTENANCE_MODE = "E9007"
    
    # Business Logic Errors (10000-10999)
    RESUME_SESSION_EXPIRED = "E10000"
    ANALYSIS_ALREADY_EXISTS = "E10001"
    INVALID_OPERATION_STATE = "E10002"
    BUSINESS_RULE_VIOLATION = "E10003"
    WORKFLOW_ERROR = "E10004"
    DATA_CONSISTENCY_ERROR = "E10005"


# Error code to category mapping
ERROR_CATEGORIES: Dict[ErrorCode, ErrorCategory] = {
    # Validation errors
    ErrorCode.VALIDATION_FAILED: ErrorCategory.VALIDATION,
    ErrorCode.INVALID_INPUT_FORMAT: ErrorCategory.VALIDATION,
    ErrorCode.MISSING_REQUIRED_FIELD: ErrorCategory.VALIDATION,
    ErrorCode.FIELD_TOO_SHORT: ErrorCategory.VALIDATION,
    ErrorCode.FIELD_TOO_LONG: ErrorCategory.VALIDATION,
    ErrorCode.INVALID_EMAIL_FORMAT: ErrorCategory.VALIDATION,
    ErrorCode.INVALID_PHONE_FORMAT: ErrorCategory.VALIDATION,
    ErrorCode.INVALID_DATE_FORMAT: ErrorCategory.VALIDATION,
    ErrorCode.INVALID_JSON_FORMAT: ErrorCategory.VALIDATION,
    ErrorCode.INVALID_CONTENT_TYPE: ErrorCategory.VALIDATION,
    
    # File processing errors
    ErrorCode.FILE_NOT_PROVIDED: ErrorCategory.FILE_PROCESSING,
    ErrorCode.FILE_TOO_LARGE: ErrorCategory.FILE_PROCESSING,
    ErrorCode.FILE_TOO_SMALL: ErrorCategory.FILE_PROCESSING,
    ErrorCode.INVALID_FILE_TYPE: ErrorCategory.FILE_PROCESSING,
    ErrorCode.FILE_CORRUPTED: ErrorCategory.FILE_PROCESSING,
    ErrorCode.FILE_PROCESSING_FAILED: ErrorCategory.FILE_PROCESSING,
    ErrorCode.FILE_UPLOAD_FAILED: ErrorCategory.FILE_PROCESSING,
    ErrorCode.FILE_NOT_FOUND: ErrorCategory.FILE_PROCESSING,
    ErrorCode.FILE_PERMISSION_DENIED: ErrorCategory.FILE_PROCESSING,
    ErrorCode.UNSUPPORTED_FILE_FORMAT: ErrorCategory.FILE_PROCESSING,
    
    # AI analysis errors
    ErrorCode.AI_SERVICE_UNAVAILABLE: ErrorCategory.AI_ANALYSIS,
    ErrorCode.AI_ANALYSIS_FAILED: ErrorCategory.AI_ANALYSIS,
    ErrorCode.AI_QUOTA_EXCEEDED: ErrorCategory.AI_ANALYSIS,
    ErrorCode.AI_TIMEOUT: ErrorCategory.AI_ANALYSIS,
    ErrorCode.INVALID_ANALYSIS_REQUEST: ErrorCategory.AI_ANALYSIS,
    ErrorCode.ANALYSIS_IN_PROGRESS: ErrorCategory.AI_ANALYSIS,
    ErrorCode.ANALYSIS_NOT_FOUND: ErrorCategory.AI_ANALYSIS,
    ErrorCode.INSUFFICIENT_CONTENT: ErrorCategory.AI_ANALYSIS,
    ErrorCode.AI_MODEL_ERROR: ErrorCategory.AI_ANALYSIS,
    ErrorCode.ANALYSIS_EXPIRED: ErrorCategory.AI_ANALYSIS,
    
    # Rate limiting errors
    ErrorCode.RATE_LIMIT_EXCEEDED: ErrorCategory.RATE_LIMITING,
    ErrorCode.TOO_MANY_REQUESTS: ErrorCategory.RATE_LIMITING,
    ErrorCode.QUOTA_EXCEEDED: ErrorCategory.RATE_LIMITING,
    ErrorCode.REQUEST_BLOCKED: ErrorCategory.RATE_LIMITING,
    ErrorCode.CLIENT_BANNED: ErrorCategory.RATE_LIMITING,
    ErrorCode.CONCURRENT_LIMIT_EXCEEDED: ErrorCategory.RATE_LIMITING,
    
    # Authentication & authorization errors
    ErrorCode.AUTHENTICATION_REQUIRED: ErrorCategory.AUTHENTICATION,
    ErrorCode.INVALID_CREDENTIALS: ErrorCategory.AUTHENTICATION,
    ErrorCode.TOKEN_EXPIRED: ErrorCategory.AUTHENTICATION,
    ErrorCode.TOKEN_INVALID: ErrorCategory.AUTHENTICATION,
    ErrorCode.INSUFFICIENT_PERMISSIONS: ErrorCategory.AUTHORIZATION,
    ErrorCode.ACCOUNT_DISABLED: ErrorCategory.AUTHENTICATION,
    ErrorCode.SESSION_EXPIRED: ErrorCategory.AUTHENTICATION,
    
    # Security errors
    ErrorCode.SECURITY_VIOLATION: ErrorCategory.SECURITY,
    ErrorCode.SUSPICIOUS_ACTIVITY: ErrorCategory.SECURITY,
    ErrorCode.MALICIOUS_CONTENT_DETECTED: ErrorCategory.SECURITY,
    ErrorCode.XSS_ATTEMPT_BLOCKED: ErrorCategory.SECURITY,
    ErrorCode.SQL_INJECTION_BLOCKED: ErrorCategory.SECURITY,
    ErrorCode.UNSAFE_FILE_DETECTED: ErrorCategory.SECURITY,
    ErrorCode.IP_BLOCKED: ErrorCategory.SECURITY,
    ErrorCode.CSRF_TOKEN_INVALID: ErrorCategory.SECURITY,
    
    # Database errors
    ErrorCode.DATABASE_CONNECTION_FAILED: ErrorCategory.DATABASE,
    ErrorCode.DATABASE_QUERY_FAILED: ErrorCategory.DATABASE,
    ErrorCode.RECORD_NOT_FOUND: ErrorCategory.DATABASE,
    ErrorCode.DUPLICATE_RECORD: ErrorCategory.DATABASE,
    ErrorCode.DATABASE_TIMEOUT: ErrorCategory.DATABASE,
    ErrorCode.TRANSACTION_FAILED: ErrorCategory.DATABASE,
    ErrorCode.CONSTRAINT_VIOLATION: ErrorCategory.DATABASE,
    ErrorCode.DATABASE_UNAVAILABLE: ErrorCategory.DATABASE,
    
    # Network errors
    ErrorCode.NETWORK_TIMEOUT: ErrorCategory.NETWORK,
    ErrorCode.CONNECTION_FAILED: ErrorCategory.NETWORK,
    ErrorCode.SERVICE_UNAVAILABLE: ErrorCategory.NETWORK,
    ErrorCode.EXTERNAL_API_ERROR: ErrorCategory.NETWORK,
    ErrorCode.DNS_RESOLUTION_FAILED: ErrorCategory.NETWORK,
    ErrorCode.SSL_CERTIFICATE_ERROR: ErrorCategory.NETWORK,
    
    # System errors
    ErrorCode.INTERNAL_SERVER_ERROR: ErrorCategory.SYSTEM,
    ErrorCode.SERVICE_TEMPORARILY_UNAVAILABLE: ErrorCategory.SYSTEM,
    ErrorCode.CONFIGURATION_ERROR: ErrorCategory.SYSTEM,
    ErrorCode.RESOURCE_EXHAUSTED: ErrorCategory.SYSTEM,
    ErrorCode.DISK_SPACE_FULL: ErrorCategory.SYSTEM,
    ErrorCode.MEMORY_LIMIT_EXCEEDED: ErrorCategory.SYSTEM,
    ErrorCode.CPU_LIMIT_EXCEEDED: ErrorCategory.SYSTEM,
    ErrorCode.MAINTENANCE_MODE: ErrorCategory.SYSTEM,
    
    # Business logic errors
    ErrorCode.RESUME_SESSION_EXPIRED: ErrorCategory.BUSINESS_LOGIC,
    ErrorCode.ANALYSIS_ALREADY_EXISTS: ErrorCategory.BUSINESS_LOGIC,
    ErrorCode.INVALID_OPERATION_STATE: ErrorCategory.BUSINESS_LOGIC,
    ErrorCode.BUSINESS_RULE_VIOLATION: ErrorCategory.BUSINESS_LOGIC,
    ErrorCode.WORKFLOW_ERROR: ErrorCategory.BUSINESS_LOGIC,
    ErrorCode.DATA_CONSISTENCY_ERROR: ErrorCategory.BUSINESS_LOGIC,
}


def get_error_category(error_code: ErrorCode) -> ErrorCategory:
    """
    Get the category for a given error code.
    
    Args:
        error_code: The error code to categorize
        
    Returns:
        The error category
    """
    return ERROR_CATEGORIES.get(error_code, ErrorCategory.SYSTEM)


def get_http_status_code(error_code: ErrorCode) -> int:
    """
    Get the appropriate HTTP status code for an error code.
    
    Args:
        error_code: The error code
        
    Returns:
        HTTP status code
    """
    category = get_error_category(error_code)
    
    # Map categories to HTTP status codes
    status_mapping = {
        ErrorCategory.VALIDATION: 422,  # Unprocessable Entity
        ErrorCategory.AUTHENTICATION: 401,  # Unauthorized
        ErrorCategory.AUTHORIZATION: 403,  # Forbidden
        ErrorCategory.RATE_LIMITING: 429,  # Too Many Requests
        ErrorCategory.FILE_PROCESSING: 400,  # Bad Request
        ErrorCategory.AI_ANALYSIS: 503,  # Service Unavailable
        ErrorCategory.DATABASE: 500,  # Internal Server Error
        ErrorCategory.NETWORK: 502,  # Bad Gateway
        ErrorCategory.SECURITY: 400,  # Bad Request
        ErrorCategory.SYSTEM: 500,  # Internal Server Error
        ErrorCategory.BUSINESS_LOGIC: 409,  # Conflict
    }
    
    # Special cases for specific error codes
    special_cases = {
        ErrorCode.FILE_NOT_FOUND: 404,
        ErrorCode.RECORD_NOT_FOUND: 404,
        ErrorCode.ANALYSIS_NOT_FOUND: 404,
        ErrorCode.SERVICE_UNAVAILABLE: 503,
        ErrorCode.AI_SERVICE_UNAVAILABLE: 503,
        ErrorCode.DATABASE_UNAVAILABLE: 503,
        ErrorCode.MAINTENANCE_MODE: 503,
        ErrorCode.FILE_TOO_LARGE: 413,  # Payload Too Large
        ErrorCode.INVALID_CONTENT_TYPE: 415,  # Unsupported Media Type
    }
    
    return special_cases.get(error_code, status_mapping.get(category, 500))


def is_client_error(error_code: ErrorCode) -> bool:
    """
    Check if an error code represents a client error (4xx).
    
    Args:
        error_code: The error code to check
        
    Returns:
        True if it's a client error
    """
    status_code = get_http_status_code(error_code)
    return 400 <= status_code < 500


def is_server_error(error_code: ErrorCode) -> bool:
    """
    Check if an error code represents a server error (5xx).
    
    Args:
        error_code: The error code to check
        
    Returns:
        True if it's a server error
    """
    status_code = get_http_status_code(error_code)
    return 500 <= status_code < 600


def should_log_error(error_code: ErrorCode) -> bool:
    """
    Determine if an error should be logged based on its code.
    
    Args:
        error_code: The error code to check
        
    Returns:
        True if the error should be logged
    """
    # Always log server errors and security violations
    if is_server_error(error_code) or get_error_category(error_code) == ErrorCategory.SECURITY:
        return True
    
    # Log certain client errors that might indicate issues
    important_client_errors = {
        ErrorCode.RATE_LIMIT_EXCEEDED,
        ErrorCode.FILE_TOO_LARGE,
        ErrorCode.MALICIOUS_CONTENT_DETECTED,
        ErrorCode.SUSPICIOUS_ACTIVITY,
        ErrorCode.AI_QUOTA_EXCEEDED,
    }
    
    return error_code in important_client_errors


def get_retry_after_seconds(error_code: ErrorCode) -> Optional[int]:
    """
    Get the retry-after seconds for rate limiting errors.
    
    Args:
        error_code: The error code
        
    Returns:
        Seconds to wait before retrying, or None if not applicable
    """
    retry_mapping = {
        ErrorCode.RATE_LIMIT_EXCEEDED: 60,
        ErrorCode.TOO_MANY_REQUESTS: 60,
        ErrorCode.AI_QUOTA_EXCEEDED: 3600,  # 1 hour
        ErrorCode.SERVICE_TEMPORARILY_UNAVAILABLE: 300,  # 5 minutes
        ErrorCode.AI_SERVICE_UNAVAILABLE: 300,
        ErrorCode.DATABASE_UNAVAILABLE: 60,
        ErrorCode.MAINTENANCE_MODE: 1800,  # 30 minutes
    }
    
    return retry_mapping.get(error_code)