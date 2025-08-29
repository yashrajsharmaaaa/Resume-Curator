"""
Security module for Resume Curator backend.

This module provides comprehensive security features including CORS configuration,
HTTPS enforcement, request limits, and session management.
"""

from .cors_config import setup_cors
from .https_enforcer import HTTPSEnforcer
from .request_limiter import RequestLimiter
from .session_manager import SessionManager
from .security_middleware import SecurityMiddleware, setup_security_middleware

__all__ = [
    'setup_cors',
    'HTTPSEnforcer',
    'RequestLimiter', 
    'SessionManager',
    'SecurityMiddleware',
    'setup_security_middleware'
]