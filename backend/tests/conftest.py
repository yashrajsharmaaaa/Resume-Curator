"""
Pytest configuration and fixtures for Resume Curator tests.

This module provides shared fixtures and configuration for all tests
including database setup, test client, and mock data.
"""

import os
import pytest
import tempfile
from typing import Generator
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import get_db
from models import Base


# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def test_db():
    """Create test database tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    """Create a fresh database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client():
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_resume_text():
    """Sample resume text for testing."""
    return """
    John Doe
    Software Engineer
    Email: john.doe@email.com
    Phone: (555) 123-4567
    
    EXPERIENCE
    Senior Software Engineer - Tech Corp (2020-2023)
    - Developed web applications using Python and React
    - Led a team of 5 developers
    - Implemented CI/CD pipelines
    
    Software Engineer - StartupCo (2018-2020)
    - Built REST APIs using FastAPI
    - Worked with PostgreSQL databases
    - Collaborated with cross-functional teams
    
    EDUCATION
    Bachelor of Science in Computer Science
    University of Technology (2014-2018)
    
    SKILLS
    - Python, JavaScript, React, FastAPI
    - PostgreSQL, MongoDB
    - Docker, Kubernetes
    - Git, CI/CD
    """


@pytest.fixture
def sample_job_description():
    """Sample job description for testing."""
    return """
    We are looking for a Senior Software Engineer to join our team.
    
    RESPONSIBILITIES:
    - Design and develop scalable web applications
    - Work with modern frameworks like React and FastAPI
    - Collaborate with product and design teams
    - Mentor junior developers
    
    REQUIREMENTS:
    - 3+ years of experience in software development
    - Strong knowledge of Python and JavaScript
    - Experience with databases (PostgreSQL preferred)
    - Familiarity with cloud platforms (AWS, GCP)
    - Experience with containerization (Docker)
    
    NICE TO HAVE:
    - Experience with Kubernetes
    - Knowledge of machine learning
    - Open source contributions
    """


@pytest.fixture
def sample_pdf_content():
    """Sample PDF content for testing."""
    # This is a minimal PDF header - in real tests you'd use a proper PDF
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"


@pytest.fixture
def sample_docx_content():
    """Sample DOCX content for testing."""
    # This is a minimal DOCX header - in real tests you'd use a proper DOCX
    return b"PK\x03\x04\x14\x00\x00\x00\x08\x00"


@pytest.fixture
def mock_ai_service():
    """Mock AI service for testing."""
    mock = AsyncMock()
    mock.analyze_resume.return_value = {
        "success": True,
        "analysis_data": {
            "compatibility_score": 85.5,
            "overall_assessment": "Strong candidate with relevant experience",
            "strengths": ["Python experience", "FastAPI knowledge", "Team leadership"],
            "areas_for_improvement": ["Cloud platform experience", "Machine learning knowledge"],
            "missing_skills": ["AWS", "Kubernetes"],
            "recommendations": ["Add cloud certifications", "Highlight specific projects"]
        },
        "processing_time_ms": 1500,
        "model_used": "openai/gpt-oss-20b",
        "timestamp": "2024-01-01T12:00:00"
    }
    mock.test_connection.return_value = {
        "success": True,
        "message": "AtlasCloud API connection successful"
    }
    return mock


@pytest.fixture
def mock_file_upload():
    """Mock file upload for testing."""
    mock_file = MagicMock()
    mock_file.filename = "test_resume.pdf"
    mock_file.content_type = "application/pdf"
    mock_file.file.read.return_value = b"%PDF-1.4\nTest PDF content"
    mock_file.read.return_value = b"%PDF-1.4\nTest PDF content"
    return mock_file


@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ["ATLASCLOUD_API_KEY"] = "test_api_key"
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    os.environ["DEBUG"] = "true"
    yield
    # Cleanup is handled by pytest


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        yield tmp.name
    os.unlink(tmp.name)


# Test data fixtures
@pytest.fixture
def valid_analysis_request():
    """Valid analysis request data."""
    return {
        "resume_id": 1,
        "job_description": "We are looking for a Python developer with FastAPI experience."
    }


@pytest.fixture
def invalid_analysis_request():
    """Invalid analysis request data."""
    return {
        "resume_id": 999,  # Non-existent resume
        "job_description": "Short"  # Too short
    }


# Mock external dependencies
@pytest.fixture(autouse=True)
def mock_external_services(monkeypatch):
    """Mock external services for all tests."""
    # Mock AtlasCloud API calls
    async def mock_analyze_resume(*args, **kwargs):
        return {
            "success": True,
            "analysis_data": {"compatibility_score": 75.0},
            "processing_time_ms": 1000
        }
    
    async def mock_test_ai_service():
        return {"success": True}
    
    monkeypatch.setattr("ai_service.analyze_resume", mock_analyze_resume)
    monkeypatch.setattr("ai_service.test_ai_service", mock_test_ai_service)
    
    # Mock file processing
    async def mock_extract_text(*args, **kwargs):
        return "Extracted text content from file"
    
    monkeypatch.setattr("file_processing.extract_text_from_file", mock_extract_text)
    
    # Mock database health check
    def mock_db_health():
        return {"status": "connected", "database": "connected"}
    
    monkeypatch.setattr("database.check_database_health", mock_db_health)