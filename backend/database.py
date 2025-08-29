"""
Database connection and session management for Resume Curator.

This module provides SQLite database connection setup, session management,
and initialization utilities using SQLAlchemy. Designed for SDE1 portfolio
demonstration with proper connection pooling and error handling.
"""

import os
from typing import Generator
from datetime import datetime
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from models import Base
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./resume_curator.db"  # Default to SQLite for development
)

# Create SQLAlchemy engine with appropriate configuration
if DATABASE_URL.startswith("sqlite"):
    # SQLite-specific configuration
    engine = create_engine(
        DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},  # Allow SQLite to be used with FastAPI
        echo=os.getenv("SQL_DEBUG", "false").lower() == "true"  # SQL logging for development
    )
else:
    # PostgreSQL configuration for production
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=3600,   # Recycle connections every hour
        echo=os.getenv("SQL_DEBUG", "false").lower() == "true"  # SQL logging for development
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """
    Create all database tables.
    
    This function creates all tables defined in the models module.
    Safe to call multiple times - will only create missing tables.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    This function provides a database session for FastAPI dependency injection.
    Ensures proper session cleanup after each request.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_database():
    """
    Initialize the database with tables and any required setup.
    
    This function should be called during application startup to ensure
    the database is properly configured.
    """
    try:
        # Test database connection
        with engine.connect() as connection:
            logger.info("Database connection successful")
        
        # Create tables
        create_tables()
        
        logger.info("Database initialization completed")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def check_database_health() -> dict:
    """
    Check database connection health.
    
    Returns:
        dict: Database health status information
    """
    try:
        with engine.connect() as connection:
            # Simple query to test connection
            from sqlalchemy import text
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
            
            return {
                "status": "connected",
                "timestamp": datetime.utcnow().isoformat(),
                "url": DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else "localhost"
            }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# Event listeners for connection management
@event.listens_for(engine, "connect")
def set_database_pragma(dbapi_connection, connection_record):
    """
    Set database-specific configuration on connection.
    
    For SQLite, enables foreign key constraints and WAL mode.
    For PostgreSQL, sets timezone configuration.
    """
    if "sqlite" in DATABASE_URL:
        # SQLite-specific settings
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")  # Enable foreign key constraints
            cursor.execute("PRAGMA journal_mode=WAL")  # Enable WAL mode for better concurrency
            cursor.close()
        except Exception as e:
            logger.debug(f"Could not set SQLite pragmas: {e}")
    elif "postgresql" in DATABASE_URL:
        # Set timezone for PostgreSQL connections
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("SET timezone TO 'UTC'")
            cursor.close()
        except Exception as e:
            logger.debug(f"Could not set timezone: {e}")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log database connection checkout for monitoring."""
    logger.debug("Database connection checked out")


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log database connection checkin for monitoring."""
    logger.debug("Database connection checked in")