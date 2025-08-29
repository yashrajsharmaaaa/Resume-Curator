"""
HTTPS enforcement middleware for secure API communication.

This module provides middleware to enforce HTTPS connections and redirect
HTTP requests to HTTPS in production environments.
"""

import os
import logging
from typing import Callable, Optional
from fastapi import Request, Response, HTTPException
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Configure logging
logger = logging.getLogger(__name__)


class HTTPSEnforcer(BaseHTTPMiddleware):
    """
    Middleware to enforce HTTPS connections.
    
    In production mode, redirects HTTP requests to HTTPS and adds
    security headers to all responses.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        enforce_https: Optional[bool] = None,
        redirect_http: bool = True,
        hsts_max_age: int = 31536000,  # 1 year
        include_subdomains: bool = True
    ):
        """
        Initialize HTTPS enforcer.
        
        Args:
            app: ASGI application
            enforce_https: Whether to enforce HTTPS (auto-detect if None)
            redirect_http: Whether to redirect HTTP to HTTPS
            hsts_max_age: HSTS max-age in seconds
            include_subdomains: Whether to include subdomains in HSTS
        """
        super().__init__(app)
        
        # Auto-detect enforcement based on environment
        if enforce_https is None:
            self.enforce_https = os.getenv("ENVIRONMENT") == "production"
        else:
            self.enforce_https = enforce_https
        
        self.redirect_http = redirect_http
        self.hsts_max_age = hsts_max_age
        self.include_subdomains = include_subdomains
        
        # Build HSTS header value
        self.hsts_header = f"max-age={hsts_max_age}"
        if include_subdomains:
            self.hsts_header += "; includeSubDomains"
        
        logger.info(f"HTTPS enforcer initialized (enforce: {self.enforce_https})")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and enforce HTTPS if required."""
        
        # Check if request is secure
        is_secure = self._is_secure_request(request)
        
        # Enforce HTTPS if required
        if self.enforce_https and not is_secure:
            if self.redirect_http:
                # Redirect to HTTPS
                https_url = self._get_https_url(request)
                logger.info(f"Redirecting HTTP request to HTTPS: {https_url}")
                return RedirectResponse(url=https_url, status_code=301)
            else:
                # Reject HTTP requests
                logger.warning(f"Rejected insecure HTTP request: {request.url}")
                raise HTTPException(
                    status_code=426,
                    detail="HTTPS required. Please use HTTPS to access this API."
                )
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        self._add_security_headers(response, is_secure)
        
        return response
    
    def _is_secure_request(self, request: Request) -> bool:
        """Check if request is using HTTPS."""
        # Check URL scheme
        if request.url.scheme == "https":
            return True
        
        # Check forwarded headers (for reverse proxies)
        forwarded_proto = request.headers.get("x-forwarded-proto", "").lower()
        if forwarded_proto == "https":
            return True
        
        # Check other proxy headers
        forwarded_ssl = request.headers.get("x-forwarded-ssl", "").lower()
        if forwarded_ssl in ("on", "1", "true"):
            return True
        
        # Check if behind a secure proxy
        if request.headers.get("x-forwarded-for") and os.getenv("TRUST_PROXY_HEADERS") == "true":
            # If we trust proxy headers and request is forwarded, assume secure
            return True
        
        return False
    
    def _get_https_url(self, request: Request) -> str:
        """Convert HTTP URL to HTTPS."""
        url = str(request.url)
        if url.startswith("http://"):
            return url.replace("http://", "https://", 1)
        return url
    
    def _add_security_headers(self, response: Response, is_secure: bool) -> None:
        """Add security headers to response."""
        
        # HSTS header (only for HTTPS responses)
        if is_secure and self.enforce_https:
            response.headers["Strict-Transport-Security"] = self.hsts_header
        
        # Content Security Policy
        csp_policy = self._get_csp_policy()
        if csp_policy:
            response.headers["Content-Security-Policy"] = csp_policy
        
        # X-Content-Type-Options
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-Frame-Options
        response.headers["X-Frame-Options"] = "DENY"
        
        # X-XSS-Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=()"
        )
        
        # Server header removal/modification
        response.headers["Server"] = "Resume-Curator-API"
    
    def _get_csp_policy(self) -> str:
        """Get Content Security Policy."""
        # Basic CSP for API responses
        policy_parts = [
            "default-src 'none'",
            "frame-ancestors 'none'",
            "base-uri 'none'",
            "form-action 'none'"
        ]
        
        # Allow specific origins for API responses if needed
        allowed_origins = os.getenv("ALLOWED_ORIGINS", "")
        if allowed_origins:
            origins = [origin.strip() for origin in allowed_origins.split(",")]
            if origins:
                connect_src = "connect-src " + " ".join(origins)
                policy_parts.append(connect_src)
        
        return "; ".join(policy_parts)


def create_https_enforcer(
    enforce_https: Optional[bool] = None,
    redirect_http: bool = True,
    hsts_max_age: int = 31536000,
    include_subdomains: bool = True
) -> type:
    """
    Create HTTPS enforcer middleware class with custom configuration.
    
    Args:
        enforce_https: Whether to enforce HTTPS
        redirect_http: Whether to redirect HTTP to HTTPS
        hsts_max_age: HSTS max-age in seconds
        include_subdomains: Whether to include subdomains in HSTS
        
    Returns:
        Configured HTTPSEnforcer class
    """
    class ConfiguredHTTPSEnforcer(HTTPSEnforcer):
        def __init__(self, app: ASGIApp):
            super().__init__(
                app=app,
                enforce_https=enforce_https,
                redirect_http=redirect_http,
                hsts_max_age=hsts_max_age,
                include_subdomains=include_subdomains
            )
    
    return ConfiguredHTTPSEnforcer


def check_https_config() -> dict:
    """
    Check HTTPS configuration and return status.
    
    Returns:
        Dictionary with HTTPS configuration status
    """
    environment = os.getenv("ENVIRONMENT", "development")
    trust_proxy = os.getenv("TRUST_PROXY_HEADERS", "false").lower() == "true"
    
    return {
        "environment": environment,
        "https_enforced": environment == "production",
        "trust_proxy_headers": trust_proxy,
        "hsts_enabled": environment == "production",
        "security_headers_enabled": True
    }