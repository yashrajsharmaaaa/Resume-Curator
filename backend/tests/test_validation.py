"""
Validation tests for Resume Curator application.

This module contains comprehensive tests for input validation including
file validation, job description validation, rate limiting, and security checks.
"""

import pytest
import time
from unittest.mock import MagicMock, patch

from validation import (
    validate_file_upload, validate_job_description, check_rate_limit,
    sanitize_text_input, sanitize_filename, create_validation_error,
    rate_limiter, get_client_id
)
from tests.test_utils import create_mock_upload_file, create_sample_pdf_content


class TestFileValidation:
    """Test cases for file upload validation."""
    
    def test_validate_valid_pdf(self):
        """Test validation of a valid PDF file."""
        mock_file = create_mock_upload_file(
            filename="resume.pdf",
            content=create_sample_pdf_content(),
            content_type="application/pdf"
        )
        
        result = validate_file_upload(mock_file)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.metadata["filename"] == "resume.pdf"
        assert result.metadata["file_extension"] == ".pdf"
    
    def test_validate_valid_docx(self):
        """Test validation of a valid DOCX file."""
        mock_file = create_mock_upload_file(
            filename="resume.docx",
            content=b"PK\x03\x04\x14\x00\x00\x00\x08\x00",  # DOCX signature
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        result = validate_file_upload(mock_file)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.metadata["filename"] == "resume.docx"
        assert result.metadata["file_extension"] == ".docx"
    
    def test_validate_no_file(self):
        """Test validation when no file is provided."""
        result = validate_file_upload(None)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FILE_REQUIRED"
        assert result.errors[0].field == "file"
    
    def test_validate_no_filename(self):
        """Test validation when file has no filename."""
        mock_file = MagicMock()
        mock_file.filename = None
        
        result = validate_file_upload(mock_file)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FILE_REQUIRED"
        assert result.errors[0].field == "filename"
    
    def test_validate_invalid_extension(self):
        """Test validation of file with invalid extension."""
        mock_file = create_mock_upload_file(
            filename="resume.txt",
            content=b"Plain text content",
            content_type="text/plain"
        )
        
        result = validate_file_upload(mock_file)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "INVALID_FILE_TYPE"
        assert ".pdf, .doc, .docx" in result.errors[0].message
    
    def test_validate_empty_file(self):
        """Test validation of empty file."""
        mock_file = create_mock_upload_file(
            filename="resume.pdf",
            content=b"",
            content_type="application/pdf"
        )
        
        result = validate_file_upload(mock_file)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FILE_EMPTY"
    
    def test_validate_oversized_file(self):
        """Test validation of file exceeding size limit."""
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        mock_file = create_mock_upload_file(
            filename="large_resume.pdf",
            content=large_content,
            content_type="application/pdf"
        )
        
        result = validate_file_upload(mock_file)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FILE_TOO_LARGE"
        assert "10MB" in result.errors[0].message
    
    def test_validate_invalid_pdf_content(self):
        """Test validation of file with invalid PDF content."""
        mock_file = create_mock_upload_file(
            filename="fake.pdf",
            content=b"This is not a PDF file",
            content_type="application/pdf"
        )
        
        result = validate_file_upload(mock_file)
        
        assert result.is_valid is False
        assert any(error.code == "INVALID_PDF" for error in result.errors)
    
    def test_validate_invalid_docx_content(self):
        """Test validation of file with invalid DOCX content."""
        mock_file = create_mock_upload_file(
            filename="fake.docx",
            content=b"This is not a DOCX file",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        result = validate_file_upload(mock_file)
        
        assert result.is_valid is False
        assert any(error.code == "INVALID_DOCX" for error in result.errors)
    
    def test_validate_suspicious_content(self):
        """Test validation of file with suspicious content."""
        suspicious_content = b"%PDF-1.4\n<script>alert('xss')</script>"
        mock_file = create_mock_upload_file(
            filename="malicious.pdf",
            content=suspicious_content,
            content_type="application/pdf"
        )
        
        result = validate_file_upload(mock_file)
        
        assert result.is_valid is False
        assert any(error.code == "SECURITY_VIOLATION" for error in result.errors)
    
    def test_validate_mime_type_mismatch(self):
        """Test validation when MIME type doesn't match extension."""
        mock_file = create_mock_upload_file(
            filename="resume.pdf",
            content=b"PK\x03\x04",  # ZIP/DOCX signature
            content_type="application/pdf"
        )
        
        result = validate_file_upload(mock_file)
        
        # Should have warnings about MIME type mismatch
        assert len(result.warnings) > 0 or len(result.errors) > 0
    
    def test_validate_file_read_error(self):
        """Test validation when file reading fails."""
        mock_file = MagicMock()
        mock_file.filename = "resume.pdf"
        mock_file.content_type = "application/pdf"
        mock_file.file.read.side_effect = Exception("Read error")
        
        result = validate_file_upload(mock_file)
        
        assert result.is_valid is False
        assert any(error.code == "FILE_READ_ERROR" for error in result.errors)


class TestJobDescriptionValidation:
    """Test cases for job description validation."""
    
    def test_validate_valid_job_description(self):
        """Test validation of a valid job description."""
        job_desc = """
        We are looking for a Senior Software Engineer to join our team.
        
        Requirements:
        - 5+ years of experience in software development
        - Strong knowledge of Python and JavaScript
        - Experience with databases and cloud platforms
        """
        
        result = validate_job_description(job_desc)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.metadata["word_count"] > 20
        assert "sanitized_content" in result.metadata
    
    def test_validate_empty_job_description(self):
        """Test validation of empty job description."""
        result = validate_job_description("")
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "REQUIRED"
    
    def test_validate_whitespace_only_job_description(self):
        """Test validation of job description with only whitespace."""
        result = validate_job_description("   \n\t   ")
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "REQUIRED"
    
    def test_validate_too_short_job_description(self):
        """Test validation of job description that's too short."""
        result = validate_job_description("Short")
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "TOO_SHORT"
    
    def test_validate_too_long_job_description(self):
        """Test validation of job description that's too long."""
        long_desc = "x" * 10001  # Exceeds 10,000 character limit
        result = validate_job_description(long_desc)
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "TOO_LONG"
    
    def test_validate_short_job_description_warning(self):
        """Test validation warning for short but valid job description."""
        short_desc = "Looking for Python developer with experience."
        result = validate_job_description(short_desc)
        
        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert any(warning.code == "SHORT_DESCRIPTION" for warning in result.warnings)
    
    def test_job_description_sanitization(self):
        """Test that job description is properly sanitized."""
        malicious_desc = """
        <script>alert('xss')</script>
        We are looking for a developer with javascript: experience.
        Requirements include on-site work.
        """
        
        result = validate_job_description(malicious_desc)
        
        assert result.is_valid is True
        sanitized = result.metadata["sanitized_content"]
        assert "<script>" not in sanitized
        assert "javascript:" not in sanitized
    
    def test_job_description_metadata(self):
        """Test that job description validation includes proper metadata."""
        job_desc = "We need a Python developer with FastAPI experience and database knowledge."
        
        result = validate_job_description(job_desc)
        
        assert result.is_valid is True
        metadata = result.metadata
        assert "word_count" in metadata
        assert "character_count" in metadata
        assert "original_length" in metadata
        assert "sanitized_length" in metadata
        assert metadata["word_count"] > 0


class TestRateLimiting:
    """Test cases for rate limiting functionality."""
    
    def setup_method(self):
        """Reset rate limiter before each test."""
        rate_limiter.clients.clear()
    
    def test_rate_limit_allows_initial_requests(self):
        """Test that initial requests are allowed."""
        mock_request = MagicMock()
        mock_request.client.host = "127.0.0.1"
        
        # Should not raise exception
        check_rate_limit(mock_request, 'default')
    
    def test_rate_limit_blocks_excessive_requests(self):
        """Test that excessive requests are blocked."""
        mock_request = MagicMock()
        mock_request.client.host = "127.0.0.1"
        
        # Make requests up to the limit
        for _ in range(60):  # Default limit is 60 per minute
            check_rate_limit(mock_request, 'default')
        
        # Next request should be blocked
        with pytest.raises(Exception) as exc_info:
            check_rate_limit(mock_request, 'default')
        
        assert "RATE_LIMIT_EXCEEDED" in str(exc_info.value)
    
    def test_rate_limit_different_endpoints(self):
        """Test rate limiting for different endpoint types."""
        mock_request = MagicMock()
        mock_request.client.host = "127.0.0.1"
        
        # Upload endpoint has lower limit (10 per minute)
        for _ in range(10):
            check_rate_limit(mock_request, 'upload')
        
        # Next request should be blocked
        with pytest.raises(Exception) as exc_info:
            check_rate_limit(mock_request, 'upload')
        
        assert "RATE_LIMIT_EXCEEDED" in str(exc_info.value)
    
    def test_rate_limit_different_clients(self):
        """Test that rate limiting is per-client."""
        mock_request1 = MagicMock()
        mock_request1.client.host = "127.0.0.1"
        
        mock_request2 = MagicMock()
        mock_request2.client.host = "192.168.1.1"
        
        # Each client should have their own limit
        for _ in range(30):
            check_rate_limit(mock_request1, 'default')
            check_rate_limit(mock_request2, 'default')
        
        # Both should still be allowed
        check_rate_limit(mock_request1, 'default')
        check_rate_limit(mock_request2, 'default')
    
    def test_rate_limit_window_expiry(self):
        """Test that rate limit window expires correctly."""
        mock_request = MagicMock()
        mock_request.client.host = "127.0.0.1"
        
        # Make requests up to limit
        for _ in range(10):
            check_rate_limit(mock_request, 'upload')
        
        # Simulate time passing (mock time)
        with patch('time.time') as mock_time:
            mock_time.return_value = time.time() + 61  # 61 seconds later
            
            # Should be allowed again
            check_rate_limit(mock_request, 'upload')
    
    def test_get_client_id(self):
        """Test client ID generation."""
        mock_request = MagicMock()
        mock_request.client.host = "127.0.0.1"
        
        client_id = get_client_id(mock_request)
        
        assert client_id == "127.0.0.1"
    
    def test_get_client_id_no_client(self):
        """Test client ID generation when no client info available."""
        mock_request = MagicMock()
        mock_request.client = None
        
        client_id = get_client_id(mock_request)
        
        assert client_id == "unknown"


class TestInputSanitization:
    """Test cases for input sanitization functions."""
    
    def test_sanitize_text_input_basic(self):
        """Test basic text sanitization."""
        text = "Hello World"
        result = sanitize_text_input(text)
        
        assert result == "Hello World"
    
    def test_sanitize_text_input_html_escape(self):
        """Test HTML escaping in text sanitization."""
        text = "<script>alert('xss')</script>"
        result = sanitize_text_input(text)
        
        assert "<script>" not in result
        assert "&lt;script&gt;" in result
    
    def test_sanitize_text_input_dangerous_patterns(self):
        """Test removal of dangerous patterns."""
        text = "javascript:alert('xss') and vbscript:msgbox('test')"
        result = sanitize_text_input(text)
        
        assert "javascript:" not in result
        assert "vbscript:" not in result
    
    def test_sanitize_text_input_whitespace_normalization(self):
        """Test whitespace normalization."""
        text = "Hello    World\n\n\nWith   extra   spaces"
        result = sanitize_text_input(text)
        
        assert "    " not in result
        assert result == "Hello World With extra spaces"
    
    def test_sanitize_text_input_max_length(self):
        """Test text truncation with max length."""
        text = "A" * 100
        result = sanitize_text_input(text, max_length=50)
        
        assert len(result) == 50
    
    def test_sanitize_text_input_empty(self):
        """Test sanitization of empty text."""
        result = sanitize_text_input("")
        assert result == ""
        
        result = sanitize_text_input(None)
        assert result == ""
    
    def test_sanitize_filename_basic(self):
        """Test basic filename sanitization."""
        filename = "resume.pdf"
        result = sanitize_filename(filename)
        
        assert result == "resume.pdf"
    
    def test_sanitize_filename_dangerous_chars(self):
        """Test removal of dangerous characters from filename."""
        filename = "resume<>:\"|?*.pdf"
        result = sanitize_filename(filename)
        
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert "|" not in result
        assert "?" not in result
        assert "*" not in result
    
    def test_sanitize_filename_path_traversal(self):
        """Test prevention of path traversal in filename."""
        filename = "../../../etc/passwd"
        result = sanitize_filename(filename)
        
        assert "../" not in result
        assert result == "passwd"
    
    def test_sanitize_filename_windows_reserved(self):
        """Test handling of Windows reserved names."""
        filename = "CON.pdf"
        result = sanitize_filename(filename)
        
        assert result.startswith("file_")
    
    def test_sanitize_filename_empty(self):
        """Test sanitization of empty filename."""
        result = sanitize_filename("")
        assert result == "unnamed_file"
        
        result = sanitize_filename(None)
        assert result == "unnamed_file"
    
    def test_sanitize_filename_too_long(self):
        """Test truncation of overly long filename."""
        long_name = "a" * 300 + ".pdf"
        result = sanitize_filename(long_name)
        
        assert len(result) <= 255
        assert result.endswith(".pdf")


class TestValidationErrors:
    """Test cases for validation error creation and handling."""
    
    def test_create_validation_error(self):
        """Test creation of validation error."""
        error = create_validation_error(
            "TEST_ERROR",
            "This is a test error",
            {"field": "test"},
            422
        )
        
        assert error.status_code == 422
        assert "TEST_ERROR" in str(error.detail)
        assert "This is a test error" in str(error.detail)
    
    def test_create_validation_error_defaults(self):
        """Test creation of validation error with defaults."""
        error = create_validation_error(
            "TEST_ERROR",
            "This is a test error"
        )
        
        assert error.status_code == 400
        assert "TEST_ERROR" in str(error.detail)


class TestSecurityValidation:
    """Test cases for security-related validation."""
    
    def test_malicious_file_content_detection(self):
        """Test detection of malicious file content."""
        malicious_content = b"<script>alert('xss')</script>"
        mock_file = create_mock_upload_file(
            filename="malicious.pdf",
            content=malicious_content,
            content_type="application/pdf"
        )
        
        result = validate_file_upload(mock_file)
        
        assert result.is_valid is False
        assert any(error.code == "SECURITY_VIOLATION" for error in result.errors)
    
    def test_javascript_injection_prevention(self):
        """Test prevention of JavaScript injection in text."""
        malicious_text = "javascript:alert('xss')"
        result = sanitize_text_input(malicious_text)
        
        assert "javascript:" not in result
    
    def test_sql_injection_prevention(self):
        """Test basic SQL injection pattern removal."""
        malicious_text = "'; DROP TABLE users; --"
        result = sanitize_text_input(malicious_text)
        
        # Basic sanitization should escape quotes
        assert "'" not in result or "&" in result  # HTML escaped
    
    def test_xss_prevention(self):
        """Test XSS prevention in text sanitization."""
        xss_text = "<img src=x onerror=alert('xss')>"
        result = sanitize_text_input(xss_text)
        
        assert "<img" not in result
        assert "onerror" not in result
        assert "&lt;img" in result  # HTML escaped