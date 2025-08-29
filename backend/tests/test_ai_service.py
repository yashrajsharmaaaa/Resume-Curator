"""
AtlasCloud AI service tests for Resume Curator application.

This module contains comprehensive tests for the AtlasCloud integration
including connection tests, analysis tests, error handling, and retry logic.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from ai_service import (
    AtlasCloudService, analyze_resume, test_ai_service, 
    get_ai_service, cleanup_ai_service
)
from tests.test_utils import TestDataGenerator, MockAtlasCloudService


class TestAtlasCloudService:
    """Test cases for the AtlasCloudService class."""
    
    @pytest.fixture
    def mock_httpx_client(self):
        """Mock httpx client for testing."""
        mock_client = AsyncMock()
        return mock_client
    
    @pytest.fixture
    def ai_service(self, mock_httpx_client):
        """Create AtlasCloudService instance with mocked client."""
        with patch('ai_service.httpx.AsyncClient', return_value=mock_httpx_client):
            service = AtlasCloudService()
            service.client = mock_httpx_client
            return service
    
    def test_service_initialization_with_api_key(self):
        """Test service initialization with valid API key."""
        with patch.dict('os.environ', {'ATLASCLOUD_API_KEY': 'test_key'}):
            service = AtlasCloudService()
            assert service.api_key == 'test_key'
            assert service.model == 'openai/gpt-oss-20b'  # Default model
    
    def test_service_initialization_without_api_key(self):
        """Test service initialization without API key raises error."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="ATLASCLOUD_API_KEY environment variable is required"):
                AtlasCloudService()
    
    def test_service_initialization_with_custom_config(self):
        """Test service initialization with custom configuration."""
        with patch.dict('os.environ', {
            'ATLASCLOUD_API_KEY': 'test_key',
            'ATLASCLOUD_MODEL': 'custom/model',
            'ATLASCLOUD_TIMEOUT': '60'
        }):
            service = AtlasCloudService()
            assert service.model == 'custom/model'
            assert service.timeout == 60
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, ai_service, mock_httpx_client):
        """Test successful API request."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Test response"
                    }
                }
            ]
        }
        mock_httpx_client.post.return_value = mock_response
        
        messages = [{"role": "user", "content": "Test message"}]
        result = await ai_service._make_request(messages)
        
        assert "choices" in result
        assert result["choices"][0]["message"]["content"] == "Test response"
        mock_httpx_client.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_make_request_http_error(self, ai_service, mock_httpx_client):
        """Test API request with HTTP error."""
        import httpx
        
        # Mock HTTP error
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        mock_httpx_client.post.side_effect = httpx.HTTPStatusError(
            "Server Error", request=MagicMock(), response=mock_response
        )
        
        messages = [{"role": "user", "content": "Test message"}]
        
        with pytest.raises(Exception, match="AtlasCloud API failed"):
            await ai_service._make_request(messages, retries=1)
    
    @pytest.mark.asyncio
    async def test_make_request_connection_error(self, ai_service, mock_httpx_client):
        """Test API request with connection error."""
        import httpx
        
        # Mock connection error
        mock_httpx_client.post.side_effect = httpx.RequestError("Connection failed")
        
        messages = [{"role": "user", "content": "Test message"}]
        
        with pytest.raises(Exception, match="AtlasCloud API failed"):
            await ai_service._make_request(messages, retries=1)
    
    @pytest.mark.asyncio
    async def test_make_request_retry_logic(self, ai_service, mock_httpx_client):
        """Test retry logic on temporary failures."""
        import httpx
        
        # Mock temporary failure then success
        mock_response_error = MagicMock()
        mock_response_error.status_code = 503
        mock_response_error.text = "Service Unavailable"
        
        mock_response_success = MagicMock()
        mock_response_success.raise_for_status.return_value = None
        mock_response_success.json.return_value = {"choices": [{"message": {"content": "Success"}}]}
        
        mock_httpx_client.post.side_effect = [
            httpx.HTTPStatusError("Service Unavailable", request=MagicMock(), response=mock_response_error),
            mock_response_success
        ]
        
        messages = [{"role": "user", "content": "Test message"}]
        
        with patch('asyncio.sleep'):  # Speed up test by mocking sleep
            result = await ai_service._make_request(messages, retries=2)
        
        assert result["choices"][0]["message"]["content"] == "Success"
        assert mock_httpx_client.post.call_count == 2
    
    @pytest.mark.asyncio
    async def test_make_request_no_retry_on_client_error(self, ai_service, mock_httpx_client):
        """Test that client errors (4xx) are not retried."""
        import httpx
        
        # Mock client error (400)
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        
        mock_httpx_client.post.side_effect = httpx.HTTPStatusError(
            "Bad Request", request=MagicMock(), response=mock_response
        )
        
        messages = [{"role": "user", "content": "Test message"}]
        
        with pytest.raises(Exception, match="AtlasCloud API failed"):
            await ai_service._make_request(messages, retries=3)
        
        # Should only be called once (no retries for 4xx errors)
        assert mock_httpx_client.post.call_count == 1


class TestAnalyzeResume:
    """Test cases for resume analysis functionality."""
    
    @pytest.fixture
    def ai_service(self):
        """Create AI service with mocked HTTP client."""
        with patch('ai_service.httpx.AsyncClient'):
            return AtlasCloudService()
    
    @pytest.mark.asyncio
    async def test_analyze_resume_success(self, ai_service):
        """Test successful resume analysis."""
        resume_text = TestDataGenerator.resume_text("normal")
        job_description = TestDataGenerator.job_description("normal")
        
        # Mock successful API response
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "compatibility_score": 85.5,
                            "overall_assessment": "Strong candidate",
                            "strengths": ["Python experience", "FastAPI knowledge"],
                            "areas_for_improvement": ["Cloud experience"],
                            "missing_skills": ["AWS", "Kubernetes"],
                            "recommendations": ["Add cloud certifications"]
                        })
                    }
                }
            ]
        }
        
        with patch.object(ai_service, '_make_request', return_value=mock_response):
            result = await ai_service.analyze_resume(resume_text, job_description)
        
        assert result["success"] is True
        assert "analysis_data" in result
        assert result["analysis_data"]["compatibility_score"] == 85.5
        assert "processing_time_ms" in result
        assert result["model_used"] == ai_service.model
    
    @pytest.mark.asyncio
    async def test_analyze_resume_without_job_description(self, ai_service):
        """Test resume analysis without job description."""
        resume_text = TestDataGenerator.resume_text("normal")
        
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "overall_score": 75.0,
                            "strengths": ["Python", "FastAPI"],
                            "recommendations": ["Add more details"]
                        })
                    }
                }
            ]
        }
        
        with patch.object(ai_service, '_make_request', return_value=mock_response):
            result = await ai_service.analyze_resume(resume_text)
        
        assert result["success"] is True
        assert "analysis_data" in result
        assert result["analysis_data"]["overall_score"] == 75.0
    
    @pytest.mark.asyncio
    async def test_analyze_resume_invalid_json_response(self, ai_service):
        """Test handling of invalid JSON response."""
        resume_text = TestDataGenerator.resume_text("normal")
        
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "This is not valid JSON"
                    }
                }
            ]
        }
        
        with patch.object(ai_service, '_make_request', return_value=mock_response):
            result = await ai_service.analyze_resume(resume_text)
        
        assert result["success"] is True
        assert "analysis_data" in result
        assert "raw_analysis" in result["analysis_data"]
        assert "parsing_error" in result["analysis_data"]
    
    @pytest.mark.asyncio
    async def test_analyze_resume_no_response_content(self, ai_service):
        """Test handling when no response content is received."""
        resume_text = TestDataGenerator.resume_text("normal")
        
        mock_response = {"choices": []}
        
        with patch.object(ai_service, '_make_request', return_value=mock_response):
            result = await ai_service.analyze_resume(resume_text)
        
        assert result["success"] is False
        assert "error" in result
        assert "No response content received" in result["error"]
    
    @pytest.mark.asyncio
    async def test_analyze_resume_api_failure(self, ai_service):
        """Test handling of API failure during analysis."""
        resume_text = TestDataGenerator.resume_text("normal")
        
        with patch.object(ai_service, '_make_request', side_effect=Exception("API Error")):
            result = await ai_service.analyze_resume(resume_text)
        
        assert result["success"] is False
        assert "error" in result
        assert "API Error" in result["error"]
        assert "processing_time_ms" in result
    
    @pytest.mark.asyncio
    async def test_analyze_resume_processing_time(self, ai_service):
        """Test that processing time is recorded."""
        resume_text = TestDataGenerator.resume_text("minimal")
        
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({"overall_score": 70.0})
                    }
                }
            ]
        }
        
        with patch.object(ai_service, '_make_request', return_value=mock_response):
            result = await ai_service.analyze_resume(resume_text)
        
        assert result["success"] is True
        assert "processing_time_ms" in result
        assert isinstance(result["processing_time_ms"], int)
        assert result["processing_time_ms"] >= 0


class TestConnectionTesting:
    """Test cases for connection testing functionality."""
    
    @pytest.fixture
    def ai_service(self):
        """Create AI service with mocked HTTP client."""
        with patch('ai_service.httpx.AsyncClient'):
            return AtlasCloudService()
    
    @pytest.mark.asyncio
    async def test_connection_success(self, ai_service):
        """Test successful connection test."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "AtlasCloud connection successful"
                    }
                }
            ]
        }
        
        with patch.object(ai_service, '_make_request', return_value=mock_response):
            result = await ai_service.test_connection()
        
        assert result["success"] is True
        assert "message" in result
        assert result["model"] == ai_service.model
    
    @pytest.mark.asyncio
    async def test_connection_failure(self, ai_service):
        """Test connection test failure."""
        with patch.object(ai_service, '_make_request', side_effect=Exception("Connection failed")):
            result = await ai_service.test_connection()
        
        assert result["success"] is False
        assert "error" in result
        assert "Connection failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_service_info(self, ai_service):
        """Test getting service information."""
        result = await ai_service.get_service_info()
        
        assert result["service"] == "AtlasCloud AI Service"
        assert result["model"] == ai_service.model
        assert result["api_key_configured"] is True
        assert result["status"] == "ready"


class TestGlobalServiceFunctions:
    """Test cases for global service functions."""
    
    @pytest.mark.asyncio
    async def test_get_ai_service(self):
        """Test getting global AI service instance."""
        with patch('ai_service.AtlasCloudService') as mock_service_class:
            mock_instance = AsyncMock()
            mock_service_class.return_value = mock_instance
            
            service1 = await get_ai_service()
            service2 = await get_ai_service()
            
            # Should return the same instance (singleton pattern)
            assert service1 is service2
            mock_service_class.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_resume_convenience_function(self):
        """Test the convenience analyze_resume function."""
        resume_text = TestDataGenerator.resume_text("minimal")
        job_description = TestDataGenerator.job_description("minimal")
        
        mock_service = AsyncMock()
        mock_service.analyze_resume.return_value = {
            "success": True,
            "analysis_data": {"compatibility_score": 80.0}
        }
        
        with patch('ai_service.get_ai_service', return_value=mock_service):
            result = await analyze_resume(resume_text, job_description)
        
        assert result["success"] is True
        assert result["analysis_data"]["compatibility_score"] == 80.0
        mock_service.analyze_resume.assert_called_once_with(resume_text, job_description)
    
    @pytest.mark.asyncio
    async def test_test_ai_service_convenience_function(self):
        """Test the convenience test_ai_service function."""
        mock_service = AsyncMock()
        mock_service.test_connection.return_value = {
            "success": True,
            "message": "Connection successful"
        }
        
        with patch('ai_service.get_ai_service', return_value=mock_service):
            result = await test_ai_service()
        
        assert result["success"] is True
        mock_service.test_connection.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_test_ai_service_exception_handling(self):
        """Test exception handling in test_ai_service function."""
        with patch('ai_service.get_ai_service', side_effect=Exception("Service error")):
            result = await test_ai_service()
        
        assert result["success"] is False
        assert "error" in result
        assert "Service error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_cleanup_ai_service(self):
        """Test AI service cleanup."""
        mock_service = AsyncMock()
        
        with patch('ai_service._ai_service', mock_service):
            await cleanup_ai_service()
            mock_service.close.assert_called_once()


class TestErrorHandling:
    """Test cases for error handling in AI service."""
    
    @pytest.fixture
    def ai_service(self):
        """Create AI service with mocked HTTP client."""
        with patch('ai_service.httpx.AsyncClient'):
            return AtlasCloudService()
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, ai_service):
        """Test handling of request timeouts."""
        import httpx
        
        with patch.object(ai_service, 'client') as mock_client:
            mock_client.post.side_effect = httpx.TimeoutException("Request timeout")
            
            result = await ai_service.analyze_resume("Test resume")
        
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self, ai_service):
        """Test handling of network errors."""
        import httpx
        
        with patch.object(ai_service, 'client') as mock_client:
            mock_client.post.side_effect = httpx.NetworkError("Network unreachable")
            
            result = await ai_service.analyze_resume("Test resume")
        
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_malformed_response_handling(self, ai_service):
        """Test handling of malformed API responses."""
        mock_response = {"invalid": "response"}  # Missing 'choices' key
        
        with patch.object(ai_service, '_make_request', return_value=mock_response):
            result = await ai_service.analyze_resume("Test resume")
        
        assert result["success"] is False
        assert "error" in result


class TestMockAtlasCloudService:
    """Test cases for the mock AtlasCloud service used in other tests."""
    
    @pytest.mark.asyncio
    async def test_mock_service_success(self):
        """Test mock service successful operation."""
        mock_service = MockAtlasCloudService(should_fail=False)
        
        result = await mock_service.analyze_resume("Test resume", "Test job")
        
        assert result["success"] is True
        assert "analysis_data" in result
        assert mock_service.call_count == 1
    
    @pytest.mark.asyncio
    async def test_mock_service_failure(self):
        """Test mock service failure simulation."""
        mock_service = MockAtlasCloudService(should_fail=True)
        
        result = await mock_service.analyze_resume("Test resume", "Test job")
        
        assert result["success"] is False
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_mock_service_connection_test(self):
        """Test mock service connection testing."""
        mock_service = MockAtlasCloudService(should_fail=False)
        
        result = await mock_service.test_connection()
        
        assert result["success"] is True
        assert "message" in result


class TestIntegrationScenarios:
    """Test cases for integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_full_analysis_workflow(self):
        """Test complete analysis workflow from start to finish."""
        resume_text = TestDataGenerator.resume_text("detailed")
        job_description = TestDataGenerator.job_description("detailed")
        
        # Mock the entire workflow
        mock_service = MockAtlasCloudService(should_fail=False)
        
        with patch('ai_service.get_ai_service', return_value=mock_service):
            result = await analyze_resume(resume_text, job_description)
        
        assert result["success"] is True
        assert "analysis_data" in result
        assert "processing_time_ms" in result
        assert result["analysis_data"]["compatibility_score"] == 85.5
    
    @pytest.mark.asyncio
    async def test_service_recovery_after_failure(self):
        """Test service recovery after temporary failure."""
        resume_text = TestDataGenerator.resume_text("normal")
        
        # First call fails, second succeeds
        mock_service = AsyncMock()
        mock_service.analyze_resume.side_effect = [
            {"success": False, "error": "Temporary failure"},
            {"success": True, "analysis_data": {"score": 75.0}}
        ]
        
        with patch('ai_service.get_ai_service', return_value=mock_service):
            # First call fails
            result1 = await analyze_resume(resume_text)
            assert result1["success"] is False
            
            # Second call succeeds
            result2 = await analyze_resume(resume_text)
            assert result2["success"] is True
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_concurrent_analysis_requests(self):
        """Test handling of concurrent analysis requests."""
        import asyncio
        
        resume_texts = [
            TestDataGenerator.resume_text("minimal"),
            TestDataGenerator.resume_text("normal"),
            TestDataGenerator.resume_text("detailed")
        ]
        
        mock_service = MockAtlasCloudService(should_fail=False)
        
        with patch('ai_service.get_ai_service', return_value=mock_service):
            # Run multiple analyses concurrently
            tasks = [analyze_resume(text) for text in resume_texts]
            results = await asyncio.gather(*tasks)
        
        # All should succeed
        for result in results:
            assert result["success"] is True
        
        # Mock service should have been called for each request
        assert mock_service.call_count == len(resume_texts)