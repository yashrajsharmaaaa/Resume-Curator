"""
Test utilities and helper functions for Resume Curator tests.

This module provides common utilities, mock data generators,
and helper functions used across multiple test modules.
"""

import json
import tempfile
from typing import Dict, Any, Optional
from unittest.mock import MagicMock

from fastapi import UploadFile
from sqlalchemy.orm import Session

from models import Resume, AnalysisResult


def create_test_resume(
    db: Session,
    filename: str = "test_resume.pdf",
    file_size: int = 1024,
    extracted_text: str = "Test resume content"
) -> Resume:
    """Create a test resume in the database."""
    resume = Resume(
        filename=filename,
        file_size=file_size,
        mime_type="application/pdf",
        extracted_text=extracted_text,
        status="completed"
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


def create_test_analysis(
    db: Session,
    resume_id: int,
    job_description: str = "Test job description",
    analysis_data: Optional[Dict[str, Any]] = None
) -> AnalysisResult:
    """Create a test analysis result in the database."""
    if analysis_data is None:
        analysis_data = {
            "compatibility_score": 75.0,
            "strengths": ["Python", "FastAPI"],
            "recommendations": ["Add more details"]
        }
    
    analysis = AnalysisResult(
        resume_id=resume_id,
        job_description=job_description,
        analysis_data=analysis_data,
        compatibility_score=75.0,
        processing_time_ms=1500
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def create_mock_upload_file(
    filename: str = "test.pdf",
    content: bytes = b"test content",
    content_type: str = "application/pdf"
) -> MagicMock:
    """Create a mock UploadFile for testing."""
    mock_file = MagicMock()
    mock_file.filename = filename
    mock_file.content_type = content_type
    
    # Create a mock file object
    mock_file_obj = MagicMock()
    mock_file_obj.read.return_value = content
    mock_file_obj.seek.return_value = None
    mock_file.file = mock_file_obj
    
    mock_file.read.return_value = content
    return mock_file


def create_temp_file(content: bytes, suffix: str = ".pdf") -> str:
    """Create a temporary file with given content."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        return tmp.name


def assert_error_response(response_data: Dict[str, Any], expected_code: str):
    """Assert that response contains expected error structure."""
    assert "error" in response_data
    error = response_data["error"]
    assert "code" in error
    assert "message" in error
    assert error["code"] == expected_code


def assert_validation_error(response_data: Dict[str, Any], field_name: str):
    """Assert that response contains validation error for specific field."""
    assert_error_response(response_data, "VALIDATION_ERROR")
    error = response_data["error"]
    if "details" in error and "errors" in error["details"]:
        errors = error["details"]["errors"]
        field_errors = [e for e in errors if e.get("field") == field_name]
        assert len(field_errors) > 0, f"No validation error found for field: {field_name}"


def create_sample_pdf_content() -> bytes:
    """Create a minimal valid PDF content for testing."""
    return b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test Resume Content) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000189 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
284
%%EOF"""


def create_sample_docx_content() -> bytes:
    """Create a minimal valid DOCX content for testing."""
    # This is a simplified DOCX structure - in real tests you'd use python-docx
    return b"PK\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00!\x00"


class MockAtlasCloudService:
    """Mock AtlasCloud service for testing."""
    
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail
        self.call_count = 0
    
    async def analyze_resume(self, resume_text: str, job_description: str = "") -> Dict[str, Any]:
        """Mock analyze_resume method."""
        self.call_count += 1
        
        if self.should_fail:
            return {
                "success": False,
                "error": "Mock AI service failure",
                "processing_time_ms": 100
            }
        
        return {
            "success": True,
            "analysis_data": {
                "compatibility_score": 85.5,
                "overall_assessment": "Strong candidate",
                "strengths": ["Python experience", "FastAPI knowledge"],
                "areas_for_improvement": ["Cloud experience"],
                "missing_skills": ["AWS", "Kubernetes"],
                "recommendations": ["Add cloud certifications"]
            },
            "processing_time_ms": 1500,
            "model_used": "openai/gpt-oss-20b"
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Mock test_connection method."""
        if self.should_fail:
            return {
                "success": False,
                "error": "Connection failed"
            }
        
        return {
            "success": True,
            "message": "AtlasCloud API connection successful"
        }


class TestDataGenerator:
    """Generate test data for various scenarios."""
    
    @staticmethod
    def resume_text(complexity: str = "normal") -> str:
        """Generate resume text of different complexities."""
        if complexity == "minimal":
            return "John Doe\nSoftware Engineer\nPython, FastAPI"
        
        elif complexity == "normal":
            return """
            John Doe
            Senior Software Engineer
            Email: john.doe@email.com
            Phone: (555) 123-4567
            
            EXPERIENCE
            Senior Software Engineer - Tech Corp (2020-2023)
            - Developed web applications using Python and React
            - Led a team of 5 developers
            
            SKILLS
            Python, JavaScript, React, FastAPI, PostgreSQL
            """
        
        elif complexity == "detailed":
            return """
            John Doe
            Senior Software Engineer
            Email: john.doe@email.com
            Phone: (555) 123-4567
            LinkedIn: linkedin.com/in/johndoe
            
            PROFESSIONAL SUMMARY
            Experienced software engineer with 5+ years of experience in full-stack development.
            Proven track record of leading teams and delivering scalable solutions.
            
            EXPERIENCE
            Senior Software Engineer - Tech Corp (2020-2023)
            - Developed and maintained web applications using Python, FastAPI, and React
            - Led a cross-functional team of 5 developers and 2 QA engineers
            - Implemented CI/CD pipelines reducing deployment time by 60%
            - Designed and optimized PostgreSQL databases handling 1M+ records
            
            Software Engineer - StartupCo (2018-2020)
            - Built REST APIs serving 10,000+ daily active users
            - Collaborated with product managers and designers on feature development
            - Implemented automated testing increasing code coverage to 90%
            
            EDUCATION
            Bachelor of Science in Computer Science
            University of Technology (2014-2018)
            GPA: 3.8/4.0
            
            SKILLS
            Languages: Python, JavaScript, TypeScript, SQL
            Frameworks: FastAPI, React, Django, Node.js
            Databases: PostgreSQL, MongoDB, Redis
            Tools: Docker, Kubernetes, Git, Jenkins
            Cloud: AWS, GCP
            """
        
        return ""
    
    @staticmethod
    def job_description(complexity: str = "normal") -> str:
        """Generate job descriptions of different complexities."""
        if complexity == "minimal":
            return "Looking for Python developer"
        
        elif complexity == "normal":
            return """
            We are looking for a Senior Software Engineer to join our team.
            
            REQUIREMENTS:
            - 3+ years of experience in software development
            - Strong knowledge of Python and JavaScript
            - Experience with databases (PostgreSQL preferred)
            - Familiarity with cloud platforms
            """
        
        elif complexity == "detailed":
            return """
            Senior Software Engineer - Full Stack Development
            
            We are seeking a talented Senior Software Engineer to join our growing engineering team.
            You will be responsible for designing, developing, and maintaining scalable web applications.
            
            RESPONSIBILITIES:
            - Design and develop scalable web applications using modern frameworks
            - Collaborate with product managers, designers, and other engineers
            - Write clean, maintainable, and well-tested code
            - Participate in code reviews and technical discussions
            - Mentor junior developers and contribute to team growth
            - Optimize application performance and scalability
            
            REQUIREMENTS:
            - Bachelor's degree in Computer Science or related field
            - 5+ years of experience in software development
            - Strong proficiency in Python and JavaScript/TypeScript
            - Experience with modern web frameworks (FastAPI, React, Django)
            - Solid understanding of database design and optimization (PostgreSQL)
            - Experience with cloud platforms (AWS, GCP, or Azure)
            - Knowledge of containerization technologies (Docker, Kubernetes)
            - Familiarity with CI/CD pipelines and DevOps practices
            - Strong problem-solving and communication skills
            
            NICE TO HAVE:
            - Experience with microservices architecture
            - Knowledge of machine learning and AI technologies
            - Open source contributions
            - Experience with high-traffic applications
            - Leadership or mentoring experience
            
            BENEFITS:
            - Competitive salary and equity package
            - Comprehensive health, dental, and vision insurance
            - Flexible work arrangements and remote work options
            - Professional development budget
            - Collaborative and inclusive work environment
            """
        
        return ""