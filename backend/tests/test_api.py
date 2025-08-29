"""
API endpoint tests for Resume Curator application.

This module contains comprehensive tests for all API endpoints including
upload, analysis, health checks, and error handling scenarios.
"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from tests.test_utils import (
    create_test_resume, create_test_analysis, create_mock_upload_file,
    assert_error_response, assert_validation_error, TestDataGenerator
)


class TestUploadEndpoint:
    def test_upload_real_pdf(self, client: TestClient, db_session):
        """Test uploading the actual Yashraj Sharma Resume.pdf file from the directory."""
        pdf_path = "../../Yashraj Sharma Resume.pdf"
        with open(pdf_path, "rb") as f:
            file_bytes = f.read()
        response = client.post(
            "/api/upload",
            files={"file": ("Yashraj Sharma Resume.pdf", file_bytes, "application/pdf")}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "Yashraj Sharma Resume.pdf"
        assert data["status"] == "completed"
        assert "upload_timestamp" in data
    """Test cases for the /api/upload endpoint."""
    
    def test_upload_valid_pdf(self, client: TestClient, db_session):
        """Test uploading a valid PDF file."""
        mock_file = create_mock_upload_file(
            filename="resume.pdf",
            content=b"%PDF-1.4\nTest PDF content",
            content_type="application/pdf"
        )
        
        with patch("api.extract_text_from_file") as mock_extract:
            mock_extract.return_value = "Extracted resume text content"
            
            response = client.post(
                "/api/upload",
                files={"file": ("resume.pdf", mock_file.read(), "application/pdf")}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] is not None
        assert data["filename"] == "resume.pdf"
        assert data["status"] == "completed"
        assert "upload_timestamp" in data
    
    def test_upload_valid_docx(self, client: TestClient, db_session):
        """Test uploading a valid DOCX file."""
        mock_file = create_mock_upload_file(
            filename="resume.docx",
            content=b"PK\x03\x04\x14\x00\x00\x00\x08\x00",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        with patch("api.extract_text_from_file") as mock_extract:
            mock_extract.return_value = "Extracted DOCX content"
            
            response = client.post(
                "/api/upload",
                files={"file": ("resume.docx", mock_file.read(), mock_file.content_type)}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "resume.docx"
    
    def test_upload_no_file(self, client: TestClient):
        """Test upload endpoint with no file provided."""
        response = client.post("/api/upload")
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data, "VALIDATION_ERROR")
    
    def test_upload_invalid_file_type(self, client: TestClient):
        """Test uploading an invalid file type."""
        response = client.post(
            "/api/upload",
            files={"file": ("resume.txt", b"Plain text content", "text/plain")}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data, "INVALID_FILE_TYPE")
    
    def test_upload_oversized_file(self, client: TestClient):
        """Test uploading a file that exceeds size limit."""
        # Create a file larger than 10MB
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        
        response = client.post(
            "/api/upload",
            files={"file": ("large_resume.pdf", large_content, "application/pdf")}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data, "FILE_TOO_LARGE")
    
    def test_upload_empty_file(self, client: TestClient):
        """Test uploading an empty file."""
        response = client.post(
            "/api/upload",
            files={"file": ("empty.pdf", b"", "application/pdf")}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data, "FILE_EMPTY")
    
    def test_upload_text_extraction_failure(self, client: TestClient):
        """Test upload when text extraction fails."""
        with patch("api.extract_text_from_file") as mock_extract:
            mock_extract.side_effect = Exception("Text extraction failed")
            
            response = client.post(
                "/api/upload",
                files={"file": ("resume.pdf", b"%PDF-1.4\nContent", "application/pdf")}
            )
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data, "TEXT_EXTRACTION_ERROR")
    
    def test_upload_insufficient_content(self, client: TestClient):
        """Test upload when extracted text is too short."""
        with patch("api.extract_text_from_file") as mock_extract:
            mock_extract.return_value = "Short"  # Less than 50 characters
            
            response = client.post(
                "/api/upload",
                files={"file": ("resume.pdf", b"%PDF-1.4\nContent", "application/pdf")}
            )
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data, "INSUFFICIENT_CONTENT")
    
    @pytest.mark.slow
    def test_upload_rate_limiting(self, client: TestClient):
        """Test rate limiting on upload endpoint."""
        # Make multiple rapid requests to trigger rate limiting
        for i in range(12):  # Exceed the limit of 10 uploads per minute
            response = client.post(
                "/api/upload",
                files={"file": (f"resume{i}.pdf", b"%PDF-1.4\nContent", "application/pdf")}
            )
            
            if response.status_code == 429:
                data = response.json()
                assert_error_response(data, "RATE_LIMIT_EXCEEDED")
                assert "retry_after" in data["error"]
                break
        else:
            pytest.fail("Rate limiting was not triggered")


class TestResumeEndpoint:
    """Test cases for the /api/resumes/{resume_id} endpoint."""
    
    def test_get_existing_resume(self, client: TestClient, db_session):
        """Test retrieving an existing resume."""
        resume = create_test_resume(db_session, filename="test.pdf")
        
        response = client.get(f"/api/resumes/{resume.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == resume.id
        assert data["filename"] == "test.pdf"
        assert data["status"] == "completed"
        assert "text_length" in data
        assert "analysis_count" in data
    
    def test_get_nonexistent_resume(self, client: TestClient):
        """Test retrieving a non-existent resume."""
        response = client.get("/api/resumes/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "Resume not found" in str(data)
    
    def test_get_resume_with_analyses(self, client: TestClient, db_session):
        """Test retrieving a resume that has analysis results."""
        resume = create_test_resume(db_session)
        analysis = create_test_analysis(db_session, resume.id)
        
        response = client.get(f"/api/resumes/{resume.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["analysis_count"] == 1


class TestAnalysisEndpoint:
    """Test cases for the /api/analyze endpoint."""
    
    def test_create_analysis_valid_request(self, client: TestClient, db_session):
        """Test creating analysis with valid request."""
        resume = create_test_resume(db_session)
        
        request_data = {
            "resume_id": resume.id,
            "job_description": TestDataGenerator.job_description("normal")
        }
        
        response = client.post("/api/analyze", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] is not None
        assert data["resume_id"] == resume.id
        assert "job_description" in data
        assert "created_at" in data
        assert data["analysis_data"]["status"] == "processing"
    
    def test_create_analysis_nonexistent_resume(self, client: TestClient):
        """Test creating analysis for non-existent resume."""
        request_data = {
            "resume_id": 999,
            "job_description": "Valid job description with sufficient length for testing purposes."
        }
        
        response = client.post("/api/analyze", json=request_data)
        
        assert response.status_code == 404
        data = response.json()
        assert "Resume not found" in str(data)
    
    def test_create_analysis_invalid_job_description(self, client: TestClient, db_session):
        """Test creating analysis with invalid job description."""
        resume = create_test_resume(db_session)
        
        request_data = {
            "resume_id": resume.id,
            "job_description": "Short"  # Too short
        }
        
        response = client.post("/api/analyze", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data, "VALIDATION_ERROR")
    
    def test_create_analysis_missing_fields(self, client: TestClient):
        """Test creating analysis with missing required fields."""
        request_data = {
            "resume_id": 1
            # Missing job_description
        }
        
        response = client.post("/api/analyze", json=request_data)
        
        assert response.status_code == 422
    
    def test_create_analysis_empty_job_description(self, client: TestClient, db_session):
        """Test creating analysis with empty job description."""
        resume = create_test_resume(db_session)
        
        request_data = {
            "resume_id": resume.id,
            "job_description": ""
        }
        
        response = client.post("/api/analyze", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        assert_error_response(data, "VALIDATION_ERROR")
    
    @pytest.mark.slow
    def test_analysis_rate_limiting(self, client: TestClient, db_session):
        """Test rate limiting on analysis endpoint."""
        resume = create_test_resume(db_session)
        
        request_data = {
            "resume_id": resume.id,
            "job_description": TestDataGenerator.job_description("normal")
        }
        
        # Make multiple rapid requests to trigger rate limiting
        for i in range(7):  # Exceed the limit of 5 analyses per 5 minutes
            response = client.post("/api/analyze", json=request_data)
            
            if response.status_code == 429:
                data = response.json()
                assert_error_response(data, "RATE_LIMIT_EXCEEDED")
                break
        else:
            pytest.fail("Rate limiting was not triggered")


class TestGetAnalysisEndpoint:
    """Test cases for the /api/analysis/{analysis_id} endpoint."""
    
    def test_get_existing_analysis(self, client: TestClient, db_session):
        """Test retrieving an existing analysis."""
        resume = create_test_resume(db_session)
        analysis = create_test_analysis(db_session, resume.id)
        
        response = client.get(f"/api/analysis/{analysis.id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == analysis.id
        assert data["resume_id"] == resume.id
        assert "analysis_data" in data
        assert "created_at" in data
    
    def test_get_nonexistent_analysis(self, client: TestClient):
        """Test retrieving a non-existent analysis."""
        response = client.get("/api/analysis/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "Analysis not found" in str(data)
    
    def test_get_analysis_with_results(self, client: TestClient, db_session):
        """Test retrieving analysis with complete results."""
        resume = create_test_resume(db_session)
        analysis_data = {
            "compatibility_score": 85.5,
            "strengths": ["Python", "FastAPI"],
            "recommendations": ["Add cloud experience"]
        }
        analysis = create_test_analysis(db_session, resume.id, analysis_data=analysis_data)
        
        response = client.get(f"/api/analysis/{analysis.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["analysis_data"]["compatibility_score"] == 85.5
        assert data["compatibility_score"] == 75.0  # From the model


class TestHealthEndpoint:
    """Test cases for the /api/health endpoint."""
    
    def test_health_check_healthy(self, client: TestClient):
        """Test health check when all services are healthy."""
        with patch("database.db_manager.test_connection") as mock_db, \
             patch("ai_service.test_ai_service") as mock_ai:
            
            mock_db.return_value = True
            mock_ai.return_value = {"success": True}
            
            response = client.get("/api/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["database"] == "connected"
            assert data["atlascloud"] == "available"
    
    def test_health_check_degraded(self, client: TestClient):
        """Test health check when some services are down."""
        with patch("database.db_manager.test_connection") as mock_db, \
             patch("ai_service.test_ai_service") as mock_ai:
            
            mock_db.return_value = True
            mock_ai.return_value = {"success": False}
            
            response = client.get("/api/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert data["database"] == "connected"
            assert data["atlascloud"] == "unavailable"
    
    def test_health_check_unhealthy(self, client: TestClient):
        """Test health check when all services are down."""
        with patch("database.db_manager.test_connection") as mock_db, \
             patch("ai_service.test_ai_service") as mock_ai:
            
            mock_db.return_value = False
            mock_ai.return_value = {"success": False}
            
            response = client.get("/api/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["database"] == "disconnected"
            assert data["atlascloud"] == "unavailable"
    
    def test_health_check_exception(self, client: TestClient):
        """Test health check when an exception occurs."""
        with patch("database.db_manager.test_connection") as mock_db:
            mock_db.side_effect = Exception("Database connection failed")
            
            response = client.get("/api/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["database"] == "error"
            assert data["atlascloud"] == "error"


class TestStatsEndpoint:
    """Test cases for the /api/stats endpoint."""
    
    def test_get_stats_empty_database(self, client: TestClient):
        """Test getting stats when database is empty."""
        response = client.get("/api/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_resumes"] == 0
        assert data["total_analyses"] == 0
        assert data["recent_resumes_24h"] == 0
        assert data["recent_analyses_24h"] == 0
        assert data["average_processing_time_ms"] == 0
        assert "timestamp" in data
    
    def test_get_stats_with_data(self, client: TestClient, db_session):
        """Test getting stats with existing data."""
        # Create test data
        resume1 = create_test_resume(db_session, filename="resume1.pdf")
        resume2 = create_test_resume(db_session, filename="resume2.pdf")
        analysis1 = create_test_analysis(db_session, resume1.id)
        analysis2 = create_test_analysis(db_session, resume2.id)
        
        response = client.get("/api/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_resumes"] == 2
        assert data["total_analyses"] == 2
        assert data["recent_resumes_24h"] == 2  # Created recently
        assert data["recent_analyses_24h"] == 2
        assert "timestamp" in data


class TestErrorHandling:
    """Test cases for error handling across all endpoints."""
    
    def test_404_endpoint(self, client: TestClient):
        """Test accessing non-existent endpoint."""
        response = client.get("/api/nonexistent")
        
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client: TestClient):
        """Test using wrong HTTP method."""
        response = client.delete("/api/upload")  # Should be POST
        
        assert response.status_code == 405
    
    def test_invalid_json(self, client: TestClient):
        """Test sending invalid JSON."""
            response = client.post(
                "/api/analyze",
                json={"invalid": "json"},
                headers={"Content-Type": "application/json"}
            )
        
        assert response.status_code == 422
    
    def test_missing_content_type(self, client: TestClient):
        """Test request without proper content type."""
        response = client.post("/api/analyze", json={"test": "data"})
        
        assert response.status_code in [400, 422]  # Depends on FastAPI version


class TestCORSHeaders:
    """Test cases for CORS headers."""
    
    def test_cors_headers_present(self, client: TestClient):
        """Test that CORS headers are present in responses."""
        response = client.options("/api/health")
        
        # Check for CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
    
    def test_preflight_request(self, client: TestClient):
        """Test CORS preflight request."""
        response = client.options(
            "/api/upload",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        assert response.status_code == 200