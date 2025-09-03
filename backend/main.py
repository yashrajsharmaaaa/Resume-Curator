

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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting Resume Curator API...")
        init_database()
        logger.info("Database initialized successfully")
        logger.info("Application startup completed")
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise
    
    yield
    
    try:
        logger.info("Shutting down Resume Curator API...")
        
        await cleanup_ai_service()
        
        logger.info("Database cleanup completed")
        
        logger.info("Application shutdown completed")
        
    except Exception as e:
        logger.error(f"Application shutdown error: {e}")


app = FastAPI(
    title="Resume Curator API",
    version="1.0.0",
    description="AI-powered resume analysis using AtlasCloud",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


cors_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
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


allowed_hosts = ["localhost", "127.0.0.1", "*.localhost"]
if os.getenv('ENVIRONMENT') == 'production':
    allowed_hosts.extend([
        "*.onrender.com",
        "resume-curator-api.onrender.com"
    ])

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
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


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
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
    
    # Force port 10000 for Render deployment
    port_env = os.getenv('PORT')
    if port_env:
        port = int(port_env)
        print(f"Using PORT from environment: {port}")
    else:
        port = 10000
        print(f"No PORT environment variable found, defaulting to: {port}")
    
    # Production settings
    reload = False if os.getenv('ENVIRONMENT') == 'production' else True
    log_level = os.getenv('LOG_LEVEL', 'info').lower()
    
    print(f"Starting Resume Curator API on {host}:{port}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"All environment variables: PORT={os.getenv('PORT')}, HOST={os.getenv('HOST')}")
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level
    )