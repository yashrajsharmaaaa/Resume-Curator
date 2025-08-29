"""
CORS (Cross-Origin Resource Sharing) configuration for secure frontend-backend communication.

This module provides secure CORS configuration that allows legitimate frontend
requests while blocking unauthorized cross-origin access.
"""

import os
import logging
from typing import List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logger = logging.getLogger(__name__)


class CORSConfig:
    """CORS configuration manager."""
    
    def __init__(self):
        """Initialize CORS configuration."""
        self.allowed_origins = self._get_allowed_origins()
        self.allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allowed_headers = [
            "Accept",
            "Accept-Language", 
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Session-ID",
            "X-Request-ID"
        ]
        self.expose_headers = [
            "X-Total-Count",
            "X-Rate-Limit-Remaining",
            "X-Rate-Limit-Reset",
            "X-Request-ID"
        ]
        self.allow_credentials = True
        self.max_age = 86400  # 24 hours
        
        logger.info(f"CORS configured with origins: {self.allowed_origins}")
    
    def _get_allowed_origins(self) -> List[str]:
        """Get allowed origins from environment variables."""
        # Default development origins
        default_origins = [
            "http://localhost:3000",  # React dev server
            "http://localhost:5173",  # Vite dev server
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173"
        ]
        
        # Get production origins from environment
        env_origins = os.getenv("ALLOWED_ORIGINS", "")
        if env_origins:
            env_origins_list = [origin.strip() for origin in env_origins.split(",")]
            # Validate origins
            validated_origins = []
            for origin in env_origins_list:
                if self._validate_origin(origin):
                    validated_origins.append(origin)
                else:
                    logger.warning(f"Invalid origin ignored: {origin}")
            
            if validated_origins:
                return validated_origins
        
        # Check if we're in production mode
        if os.getenv("ENVIRONMENT") == "production":
            logger.warning("Production mode detected but no ALLOWED_ORIGINS set. Using restrictive defaults.")
            return []  # No origins allowed in production without explicit configuration
        
        return default_origins
    
    def _validate_origin(self, origin: str) -> bool:
        """Validate origin format."""
        if not origin:
            return False
        
        # Must start with http:// or https://
        if not (origin.startswith("http://") or origin.startswith("https://")):
            return False
        
        # Should not contain wildcards in production
        if os.getenv("ENVIRONMENT") == "production" and "*" in origin:
            return False
        
        # Basic format validation
        try:
            from urllib.parse import urlparse
            parsed = urlparse(origin)
            return bool(parsed.netloc)
        except Exception:
            return False
    
    def get_cors_kwargs(self) -> dict:
        """Get CORS middleware configuration."""
        return {
            "allow_origins": self.allowed_origins,
            "allow_credentials": self.allow_credentials,
            "allow_methods": self.allowed_methods,
            "allow_headers": self.allowed_headers,
            "expose_headers": self.expose_headers,
            "max_age": self.max_age
        }


def setup_cors(app: FastAPI, custom_config: Optional[CORSConfig] = None) -> None:
    """
    Set up CORS middleware for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        custom_config: Custom CORS configuration (optional)
    """
    config = custom_config or CORSConfig()
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        **config.get_cors_kwargs()
    )
    
    logger.info("CORS middleware configured successfully")


def get_cors_headers() -> dict:
    """
    Get CORS headers for manual response handling.
    
    Returns:
        Dictionary of CORS headers
    """
    config = CORSConfig()
    
    headers = {
        "Access-Control-Allow-Methods": ", ".join(config.allowed_methods),
        "Access-Control-Allow-Headers": ", ".join(config.allowed_headers),
        "Access-Control-Expose-Headers": ", ".join(config.expose_headers),
        "Access-Control-Max-Age": str(config.max_age)
    }
    
    if config.allow_credentials:
        headers["Access-Control-Allow-Credentials"] = "true"
    
    return headers


def validate_origin(origin: str) -> bool:
    """
    Validate if an origin is allowed.
    
    Args:
        origin: Origin to validate
        
    Returns:
        True if origin is allowed, False otherwise
    """
    config = CORSConfig()
    return origin in config.allowed_origins


def is_cors_preflight(method: str, headers: dict) -> bool:
    """
    Check if request is a CORS preflight request.
    
    Args:
        method: HTTP method
        headers: Request headers
        
    Returns:
        True if preflight request, False otherwise
    """
    return (
        method == "OPTIONS" and
        "access-control-request-method" in headers
    )