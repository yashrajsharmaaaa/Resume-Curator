"""
Error logging system for Resume Curator backend.

Provides structured logging for errors and security events
without exposing sensitive information.
"""

import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, Union
from pathlib import Path

from fastapi import Request

from .error_codes import ErrorCode, ErrorCategory, get_error_category

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class ErrorLogger:
    """
    Centralized error logging with structured data and security considerations.
    """
    
    def __init__(self, log_file: Optional[str] = None, enable_file_logging: bool = True):
        self.log_file = log_file or "logs/errors.log"
        self.enable_file_logging = enable_file_logging
        self.security_log_file = "logs/security.log"
        
        # Create log directories if they don't exist
        if self.enable_file_logging:
            Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
            Path(self.security_log_file).parent.mkdir(parents=True, exist_ok=True)
    
    async def log_error(
        self,
        error_code: ErrorCode,
        message: str,
        request: Optional[Request] = None,
        exception: Optional[Exception] = None,
        additional_data: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Log an error with structured data.
        
        Args:
            error_code: The error code
            message: Error message
            request: HTTP request object
            exception: The exception that occurred
            additional_data: Additional data to log
            user_id: User ID if available
            
        Returns:
            Log entry ID
        """
        try:
            # Generate log entry ID
            log_id = self._generate_log_id()
            
            # Build log entry
            log_entry = {
                'log_id': log_id,
                'timestamp': datetime.utcnow().isoformat(),
                'level': 'ERROR',
                'error_code': error_code.value,
                'error_category': get_error_category(error_code).value,
                'message': message,
                'user_id': user_id,
            }
            
            # Add request information (sanitized)
            if request:
                log_entry['request'] = self._extract_request_info(request)
            
            # Add exception information
            if exception:
                log_entry['exception'] = self._extract_exception_info(exception)
            
            # Add additional data (sanitized)
            if additional_data:
                log_entry['additional_data'] = self._sanitize_log_data(additional_data)
            
            # Log to console
            logger.error(f"Error {error_code.value}: {message}", extra={'log_entry': log_entry})
            
            # Log to file if enabled
            if self.enable_file_logging:
                await self._write_to_file(self.log_file, log_entry)
            
            return log_id
            
        except Exception as logging_error:
            # Fallback logging if structured logging fails
            logger.error(f"Failed to log error: {logging_error}")
            logger.error(f"Original error: {error_code.value} - {message}")
            return "unknown"
    
    async def log_security_event(
        self,
        event_type: str,
        message: str,
        request: Optional[Request] = None,
        severity: str = 'medium',
        additional_data: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Log a security event with enhanced tracking.
        
        Args:
            event_type: Type of security event
            message: Event message
            request: HTTP request object
            severity: Event severity (low, medium, high, critical)
            additional_data: Additional data to log
            user_id: User ID if available
            
        Returns:
            Log entry ID
        """
        try:
            # Generate log entry ID
            log_id = self._generate_log_id()
            
            # Build security log entry
            log_entry = {
                'log_id': log_id,
                'timestamp': datetime.utcnow().isoformat(),
                'level': 'SECURITY',
                'event_type': event_type,
                'severity': severity.upper(),
                'message': message,
                'user_id': user_id,
            }
            
            # Add request information (enhanced for security)
            if request:
                log_entry['request'] = self._extract_security_request_info(request)
            
            # Add additional data (sanitized)
            if additional_data:
                log_entry['additional_data'] = self._sanitize_log_data(additional_data)
            
            # Log to console with appropriate level
            log_level = {
                'low': logging.INFO,
                'medium': logging.WARNING,
                'high': logging.ERROR,
                'critical': logging.CRITICAL
            }.get(severity.lower(), logging.WARNING)
            
            logger.log(log_level, f"Security event {event_type}: {message}", extra={'log_entry': log_entry})
            
            # Log to security file if enabled
            if self.enable_file_logging:
                await self._write_to_file(self.security_log_file, log_entry)
            
            return log_id
            
        except Exception as logging_error:
            # Fallback logging if structured logging fails
            logger.error(f"Failed to log security event: {logging_error}")
            logger.warning(f"Original security event: {event_type} - {message}")
            return "unknown"
    
    def _generate_log_id(self) -> str:
        """Generate a unique log entry ID."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _extract_request_info(self, request: Request) -> Dict[str, Any]:
        """Extract relevant request information for logging."""
        try:
            # Get client IP (handle proxies)
            client_ip = request.client.host if request.client else "unknown"
            forwarded_for = request.headers.get('x-forwarded-for')
            if forwarded_for:
                client_ip = forwarded_for.split(',')[0].strip()
            
            return {
                'method': request.method,
                'url': str(request.url),
                'path': request.url.path,
                'query_params': dict(request.query_params),
                'client_ip': self._hash_ip(client_ip),  # Hash IP for privacy
                'user_agent': request.headers.get('user-agent', 'unknown')[:200],  # Limit length
                'content_type': request.headers.get('content-type'),
                'content_length': request.headers.get('content-length'),
                'referer': request.headers.get('referer'),
                'request_id': request.headers.get('x-request-id'),
            }
        except Exception as e:
            logger.warning(f"Failed to extract request info: {e}")
            return {'error': 'failed_to_extract_request_info'}
    
    def _extract_security_request_info(self, request: Request) -> Dict[str, Any]:
        """Extract enhanced request information for security logging."""
        try:
            base_info = self._extract_request_info(request)
            
            # Add security-relevant headers
            security_headers = {
                'x-forwarded-for': request.headers.get('x-forwarded-for'),
                'x-real-ip': request.headers.get('x-real-ip'),
                'x-forwarded-proto': request.headers.get('x-forwarded-proto'),
                'origin': request.headers.get('origin'),
                'host': request.headers.get('host'),
                'accept': request.headers.get('accept'),
                'accept-language': request.headers.get('accept-language'),
                'accept-encoding': request.headers.get('accept-encoding'),
            }
            
            # Filter out None values
            security_headers = {k: v for k, v in security_headers.items() if v is not None}
            
            base_info['security_headers'] = security_headers
            return base_info
            
        except Exception as e:
            logger.warning(f"Failed to extract security request info: {e}")
            return {'error': 'failed_to_extract_security_request_info'}
    
    def _extract_exception_info(self, exception: Exception) -> Dict[str, Any]:
        """Extract relevant exception information for logging."""
        try:
            import traceback
            
            return {
                'type': type(exception).__name__,
                'message': str(exception),
                'module': getattr(exception, '__module__', 'unknown'),
                'traceback': traceback.format_exc(),
            }
        except Exception as e:
            logger.warning(f"Failed to extract exception info: {e}")
            return {'error': 'failed_to_extract_exception_info'}
    
    def _sanitize_log_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize log data to remove sensitive information."""
        try:
            sanitized = {}
            
            for key, value in data.items():
                # Skip sensitive keys
                if self._is_sensitive_key(key):
                    sanitized[key] = '[REDACTED]'
                    continue
                
                # Sanitize values
                if isinstance(value, str):
                    sanitized[key] = self._sanitize_string_value(value)
                elif isinstance(value, dict):
                    sanitized[key] = self._sanitize_log_data(value)
                elif isinstance(value, list):
                    sanitized[key] = [
                        self._sanitize_string_value(item) if isinstance(item, str) else item
                        for item in value[:10]  # Limit list length
                    ]
                else:
                    sanitized[key] = value
            
            return sanitized
            
        except Exception as e:
            logger.warning(f"Failed to sanitize log data: {e}")
            return {'error': 'failed_to_sanitize_log_data'}
    
    def _is_sensitive_key(self, key: str) -> bool:
        """Check if a key contains sensitive information."""
        sensitive_keys = {
            'password', 'passwd', 'pwd', 'secret', 'token', 'key', 'auth',
            'authorization', 'credential', 'api_key', 'access_token',
            'refresh_token', 'session_id', 'cookie', 'ssn', 'social_security',
            'credit_card', 'card_number', 'cvv', 'pin'
        }
        
        key_lower = key.lower()
        return any(sensitive in key_lower for sensitive in sensitive_keys)
    
    def _sanitize_string_value(self, value: str) -> str:
        """Sanitize string values to remove sensitive patterns."""
        if not value:
            return value
        
        # Limit length
        if len(value) > 500:
            value = value[:497] + "..."
        
        # Remove sensitive patterns
        import re
        
        # Email addresses
        value = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', value)
        
        # Phone numbers
        value = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', value)
        
        # Credit card numbers
        value = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD]', value)
        
        # Social security numbers
        value = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', value)
        
        # Potential tokens or keys (long alphanumeric strings)
        value = re.sub(r'\b[A-Za-z0-9]{32,}\b', '[TOKEN]', value)
        
        return value
    
    def _hash_ip(self, ip: str) -> str:
        """Hash IP address for privacy while maintaining uniqueness."""
        try:
            # Use SHA-256 hash with a salt for privacy
            salt = "resume_curator_ip_salt"  # In production, use a secure random salt
            return hashlib.sha256(f"{salt}{ip}".encode()).hexdigest()[:16]
        except Exception:
            return "unknown_ip"
    
    async def _write_to_file(self, file_path: str, log_entry: Dict[str, Any]) -> None:
        """Write log entry to file."""
        try:
            import aiofiles
            
            # Convert log entry to JSON
            log_line = json.dumps(log_entry, default=str) + '\n'
            
            # Write to file
            async with aiofiles.open(file_path, 'a', encoding='utf-8') as f:
                await f.write(log_line)
                
        except Exception as e:
            logger.warning(f"Failed to write to log file {file_path}: {e}")


# Global error logger instance
error_logger = ErrorLogger()


async def log_error(
    error_code: ErrorCode,
    message: str,
    request: Optional[Request] = None,
    exception: Optional[Exception] = None,
    additional_data: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None
) -> str:
    """
    Convenience function to log an error.
    
    Args:
        error_code: The error code
        message: Error message
        request: HTTP request object
        exception: The exception that occurred
        additional_data: Additional data to log
        user_id: User ID if available
        
    Returns:
        Log entry ID
    """
    return await error_logger.log_error(
        error_code=error_code,
        message=message,
        request=request,
        exception=exception,
        additional_data=additional_data,
        user_id=user_id
    )


async def log_security_event(
    event_type: str,
    message: str,
    request: Optional[Request] = None,
    severity: str = 'medium',
    additional_data: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None
) -> str:
    """
    Convenience function to log a security event.
    
    Args:
        event_type: Type of security event
        message: Event message
        request: HTTP request object
        severity: Event severity (low, medium, high, critical)
        additional_data: Additional data to log
        user_id: User ID if available
        
    Returns:
        Log entry ID
    """
    return await error_logger.log_security_event(
        event_type=event_type,
        message=message,
        request=request,
        severity=severity,
        additional_data=additional_data,
        user_id=user_id
    )