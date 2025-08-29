"""
Request size and timeout limiter for API security.

This module provides middleware to enforce request size limits and timeouts
to prevent abuse and resource exhaustion attacks.
"""

import os
import time
import logging
import asyncio
from typing import Callable, Optional, Dict, Any
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.responses import JSONResponse

# Configure logging
logger = logging.getLogger(__name__)


class RequestLimiter(BaseHTTPMiddleware):
    """
    Middleware to enforce request size limits and timeouts.
    
    Provides protection against:
    - Large request body attacks
    - Slow request attacks
    - Resource exhaustion
    """
    
    def __init__(
        self,
        app: ASGIApp,
        max_request_size: int = 10 * 1024 * 1024,  # 10MB
        request_timeout: int = 30,  # 30 seconds
        max_concurrent_requests: int = 100,
        enable_request_logging: bool = True
    ):
        """
        Initialize request limiter.
        
        Args:
            app: ASGI application
            max_request_size: Maximum request body size in bytes
            request_timeout: Request timeout in seconds
            max_concurrent_requests: Maximum concurrent requests
            enable_request_logging: Whether to log request metrics
        """
        super().__init__(app)
        
        self.max_request_size = max_request_size
        self.request_timeout = request_timeout
        self.max_concurrent_requests = max_concurrent_requests
        self.enable_request_logging = enable_request_logging
        
        # Track concurrent requests
        self.active_requests = 0
        self.request_lock = asyncio.Lock()
        
        # Request metrics
        self.request_metrics = {
            'total_requests': 0,
            'rejected_size': 0,
            'rejected_timeout': 0,
            'rejected_concurrent': 0,
            'avg_request_time': 0.0
        }
        
        logger.info(f"Request limiter initialized (max_size: {max_request_size/1024/1024:.1f}MB, timeout: {request_timeout}s)")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with size and timeout limits."""
        start_time = time.time()
        
        try:
            # Check concurrent request limit
            async with self.request_lock:
                if self.active_requests >= self.max_concurrent_requests:
                    self.request_metrics['rejected_concurrent'] += 1
                    logger.warning(f"Rejected request due to concurrent limit: {self.active_requests}")
                    return self._create_error_response(
                        status_code=429,
                        error_type="CONCURRENT_LIMIT_EXCEEDED",
                        message="Too many concurrent requests. Please try again later."
                    )
                
                self.active_requests += 1
            
            try:
                # Check request size
                content_length = request.headers.get("content-length")
                if content_length:
                    try:
                        size = int(content_length)
                        if size > self.max_request_size:
                            self.request_metrics['rejected_size'] += 1
                            logger.warning(f"Rejected request due to size: {size} bytes")
                            return self._create_error_response(
                                status_code=413,
                                error_type="REQUEST_TOO_LARGE",
                                message=f"Request body too large. Maximum size: {self.max_request_size/1024/1024:.1f}MB"
                            )
                    except ValueError:
                        pass
                
                # Process request with timeout
                try:
                    response = await asyncio.wait_for(
                        call_next(request),
                        timeout=self.request_timeout
                    )
                except asyncio.TimeoutError:
                    self.request_metrics['rejected_timeout'] += 1
                    logger.warning(f"Request timeout after {self.request_timeout}s")
                    return self._create_error_response(
                        status_code=408,
                        error_type="REQUEST_TIMEOUT",
                        message=f"Request timeout after {self.request_timeout} seconds"
                    )
                
                # Add response headers
                self._add_limit_headers(response)
                
                # Update metrics
                if self.enable_request_logging:
                    self._update_metrics(start_time)
                
                return response
                
            finally:
                # Always decrement active requests
                async with self.request_lock:
                    self.active_requests -= 1
        
        except Exception as e:
            logger.error(f"Request limiter error: {e}")
            return self._create_error_response(
                status_code=500,
                error_type="INTERNAL_ERROR",
                message="Internal server error"
            )
    
    def _create_error_response(self, status_code: int, error_type: str, message: str) -> JSONResponse:
        """Create standardized error response."""
        content = {
            "error": True,
            "error_type": error_type,
            "message": message,
            "timestamp": time.time()
        }
        
        response = JSONResponse(content=content, status_code=status_code)
        self._add_limit_headers(response)
        
        return response
    
    def _add_limit_headers(self, response: Response) -> None:
        """Add limit-related headers to response."""
        response.headers["X-Request-Size-Limit"] = str(self.max_request_size)
        response.headers["X-Request-Timeout"] = str(self.request_timeout)
        response.headers["X-Concurrent-Requests"] = str(self.active_requests)
        response.headers["X-Max-Concurrent-Requests"] = str(self.max_concurrent_requests)
    
    def _update_metrics(self, start_time: float) -> None:
        """Update request metrics."""
        request_time = time.time() - start_time
        
        self.request_metrics['total_requests'] += 1
        
        # Update average request time (simple moving average)
        total = self.request_metrics['total_requests']
        current_avg = self.request_metrics['avg_request_time']
        self.request_metrics['avg_request_time'] = (current_avg * (total - 1) + request_time) / total
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get request limiter metrics."""
        return {
            **self.request_metrics,
            'active_requests': self.active_requests,
            'max_request_size_mb': self.max_request_size / 1024 / 1024,
            'request_timeout_seconds': self.request_timeout,
            'max_concurrent_requests': self.max_concurrent_requests
        }
    
    def reset_metrics(self) -> None:
        """Reset request metrics."""
        self.request_metrics = {
            'total_requests': 0,
            'rejected_size': 0,
            'rejected_timeout': 0,
            'rejected_concurrent': 0,
            'avg_request_time': 0.0
        }
        logger.info("Request limiter metrics reset")


class FileUploadLimiter:
    """Specialized limiter for file upload endpoints."""
    
    def __init__(
        self,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        allowed_content_types: Optional[list] = None,
        max_files_per_request: int = 1
    ):
        """
        Initialize file upload limiter.
        
        Args:
            max_file_size: Maximum file size in bytes
            allowed_content_types: List of allowed content types
            max_files_per_request: Maximum files per request
        """
        self.max_file_size = max_file_size
        self.allowed_content_types = allowed_content_types or [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        self.max_files_per_request = max_files_per_request
    
    async def validate_upload(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        Validate file upload request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Error dict if validation fails, None if valid
        """
        content_type = request.headers.get("content-type", "")
        
        # Check if it's a multipart upload
        if not content_type.startswith("multipart/form-data"):
            return {
                "error_type": "INVALID_CONTENT_TYPE",
                "message": "File uploads must use multipart/form-data"
            }
        
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_file_size:
                    return {
                        "error_type": "FILE_TOO_LARGE",
                        "message": f"File size exceeds limit of {self.max_file_size/1024/1024:.1f}MB"
                    }
            except ValueError:
                pass
        
        return None
    
    def get_upload_limits(self) -> Dict[str, Any]:
        """Get upload limits information."""
        return {
            "max_file_size_bytes": self.max_file_size,
            "max_file_size_mb": self.max_file_size / 1024 / 1024,
            "allowed_content_types": self.allowed_content_types,
            "max_files_per_request": self.max_files_per_request
        }


def create_request_limiter(
    max_request_size: int = 10 * 1024 * 1024,
    request_timeout: int = 30,
    max_concurrent_requests: int = 100,
    enable_request_logging: bool = True
) -> type:
    """
    Create request limiter middleware class with custom configuration.
    
    Args:
        max_request_size: Maximum request body size in bytes
        request_timeout: Request timeout in seconds
        max_concurrent_requests: Maximum concurrent requests
        enable_request_logging: Whether to log request metrics
        
    Returns:
        Configured RequestLimiter class
    """
    class ConfiguredRequestLimiter(RequestLimiter):
        def __init__(self, app: ASGIApp):
            super().__init__(
                app=app,
                max_request_size=max_request_size,
                request_timeout=request_timeout,
                max_concurrent_requests=max_concurrent_requests,
                enable_request_logging=enable_request_logging
            )
    
    return ConfiguredRequestLimiter


def get_request_limits_from_env() -> Dict[str, int]:
    """Get request limits from environment variables."""
    return {
        "max_request_size": int(os.getenv("MAX_REQUEST_SIZE", 10 * 1024 * 1024)),
        "request_timeout": int(os.getenv("REQUEST_TIMEOUT", 30)),
        "max_concurrent_requests": int(os.getenv("MAX_CONCURRENT_REQUESTS", 100))
    }