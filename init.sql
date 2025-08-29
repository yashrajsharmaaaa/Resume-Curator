-- Resume Curator Database Initialization
-- This file is automatically executed when the PostgreSQL container starts

-- Create database (already created by POSTGRES_DB env var)
-- CREATE DATABASE resume_curator;

-- Connect to the database
\c resume_curator;

-- Create extensions that might be useful
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search

-- The application will create tables automatically using SQLModel/Alembic
-- This file is just for initial setup and extensions

-- Create a simple health check table
CREATE TABLE IF NOT EXISTS health_check (
    id SERIAL PRIMARY KEY,
    status VARCHAR(50) DEFAULT 'healthy',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO health_check (status) VALUES ('initialized');

-- Grant permissions (if needed for specific users)
-- GRANT ALL PRIVILEGES ON DATABASE resume_curator TO postgres;