"""
Resume Curator FastAPI Application

This is the main application file for the Resume Curator API.
Designed for SDE1 portfolio demonstration with clean architecture,
proper error handling, and essential middleware.
"""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from database import init_database, check_database_health
from ai_analysis_service import cleanup_ai_service
from api import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    
    Handles database initialization on startup and cleanup on shutdown.
    """
    # Startup
    try:
        logger.info("Starting Resume Curator API...")
        
        # Initialize database
        init_database()
        logger.info("Database initialized successfully")
        
        logger.info("Application startup completed")
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    try:
        logger.info("Shutting down Resume Curator API...")
        
        # Cleanup AI service
        await cleanup_ai_service()
        
        # Database cleanup handled automatically by SQLAlchemy
        logger.info("Database cleanup completed")
        
        logger.info("Application shutdown completed")
        
    except Exception as e:
        logger.error(f"Application shutdown error: {e}")


# Create FastAPI application
app = FastAPI(
    title="Resume Curator API",
    version="1.0.0",
    description="AI-powered resume analysis using AtlasCloud",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# CORS Configuration
cors_origins = [
    "http://localhost:3000",  # React development server
    "http://localhost:5173",  # Vite development server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# Add production origins from environment
cors_env = os.getenv('CORS_ORIGINS')
if cors_env:
    try:
        import json
        production_origins = json.loads(cors_env)
        cors_origins.extend(production_origins)
    except (json.JSONDecodeError, TypeError):
        logger.warning(f"Invalid CORS_ORIGINS format: {cors_env}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Trusted Host Middleware (security)
allowed_hosts = ["localhost", "127.0.0.1", "*.localhost"]

# Add production hosts
if os.getenv('ENVIRONMENT') == 'production':
    allowed_hosts.extend([
        "*.onrender.com",
        "resume-curator-api.onrender.com"
    ])

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred",
                "details": {}
            }
        }
    )


# HTTP exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handler for HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail if isinstance(exc.detail, dict) else {
            "error": {
                "code": "HTTP_ERROR",
                "message": str(exc.detail),
                "details": {}
            }
        }
    )


# Include API routes
app.include_router(router, prefix="/api")


# Root endpoint
@app.get("/")
async def read_root():
    """Root endpoint returning API information."""
    return {
        "name": "Resume Curator API",
        "version": "1.0.0",
        "description": "AI-powered resume analysis using AtlasCloud",
        "status": "running",
        "docs": "/docs"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns application and database health information.
    """
    try:
        # Test database connection
        db_health = check_database_health()
        
        # Test AI service
        from ai_analysis_service import test_ai_service
        ai_result = await test_ai_service()
        
        # Determine overall status
        db_status = "connected" if db_health.get("status") == "connected" else "disconnected"
        ai_status = "available" if ai_result.get("success") else "unavailable"
        
        overall_status = "healthy" if db_status == "connected" and ai_status == "available" else "degraded"
        
        return {
            "status": overall_status,
            "timestamp": db_health.get("timestamp", "unknown"),
            "database": db_status,
            "ai_service": ai_status,
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "database": "error",
            "ai_service": "error"
        }

if __name__ == "__main__":
    import uvicorn
    
    # Get server configuration from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 10000))  # Default to 10000 for Render
    
    # Production settings
    reload = False if os.getenv('ENVIRONMENT') == 'production' else True
    log_level = os.getenv('LOG_LEVEL', 'info').lower()
    
    print(f"Starting Resume Curator API on {host}:{port}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level
    )