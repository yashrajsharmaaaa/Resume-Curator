"""
AI service for Resume Curator application using AtlasCloud.

This module provides a clean interface for AI-powered resume analysis
using AtlasCloud's GPT models. Designed for SDE1 portfolio demonstration
with proper error handling and retry logic.
"""

import asyncio

import os
import json

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class AtlasCloudService:
    """
    AtlasCloud AI service for resume analysis.
    
    Provides a simplified interface for AI-powered resume analysis
    with proper error handling, retry logic, and response parsing.
    """
    
    def __init__(self):
        """Initialize AtlasCloud service with configuration."""
        self.api_key = os.getenv('ATLASCLOUD_API_KEY')
        self.base_url = os.getenv('ATLASCLOUD_BASE_URL', 'https://api.atlascloud.ai/v1')
        self.model = os.getenv('ATLASCLOUD_MODEL', 'openai/gpt-oss-20b')
        self.timeout = int(os.getenv('ATLASCLOUD_TIMEOUT', '30'))
        
        if not self.api_key:
            raise ValueError("ATLASCLOUD_API_KEY environment variable is required")
        
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
        )
        
        logger.info(f"AtlasCloud service initialized with model: {self.model}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def _make_request(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2048,
        retries: int = 3
    ) -> Dict[str, Any]:
        """
        Make a request to AtlasCloud API with retry logic.
        
        Args:
            messages: List of message objects
            system_prompt: System prompt for the conversation
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            retries: Number of retry attempts
            
        Returns:
            API response dictionary
            
        Raises:
            Exception: If all retry attempts fail
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "systemPrompt": system_prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 0.9,
            "top_k": 50,
            "repetition_penalty": 1.1
        }
        
        last_exception = None
        
        for attempt in range(retries):
            try:
                logger.debug(f"AtlasCloud request attempt {attempt + 1}/{retries}")
                
                response = await self.client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.debug("AtlasCloud request successful")
                return result
                
            except httpx.HTTPStatusError as e:
                last_exception = e
                logger.warning(f"AtlasCloud HTTP error (attempt {attempt + 1}): {e.response.status_code}")
                
                # Don't retry on client errors (4xx)
                if 400 <= e.response.status_code < 500:
                    break
                
                # Wait before retry
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
            except httpx.RequestError as e:
                last_exception = e
                logger.warning(f"AtlasCloud request error (attempt {attempt + 1}): {e}")
                
                # Wait before retry
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
            
            except Exception as e:
                last_exception = e
                logger.error(f"AtlasCloud unexpected error (attempt {attempt + 1}): {e}")
                break
        
        # All retries failed
        raise Exception(f"AtlasCloud API failed after {retries} attempts: {last_exception}")
    
    async def analyze_resume(
        self,
        resume_text: str,
        job_description: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze a resume using AtlasCloud AI.
        
        Args:
            resume_text: The resume content to analyze
            job_description: Optional job description for matching
            
        Returns:
            Analysis results dictionary with standardized format
        """
        start_time = datetime.utcnow()
        
        try:
            # Create system prompt
            system_prompt = """You are an expert resume analyzer and career consultant. 
            Analyze the resume and provide detailed feedback in a structured format. 
            Focus on practical, actionable insights that will help improve the resume."""
            
            # Create user message
            if job_description.strip():
                user_content = f"""Please analyze this resume against the job description:

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Provide analysis in JSON format with this structure:
{{
    "compatibility_score": <score 0-100>,
    "overall_assessment": "<brief overall assessment>",
    "strengths": ["<strength 1>", "<strength 2>", ...],
    "areas_for_improvement": ["<improvement 1>", "<improvement 2>", ...],
    "missing_skills": ["<skill 1>", "<skill 2>", ...],
    "recommendations": ["<recommendation 1>", "<recommendation 2>", ...],
    "keywords_found": ["<keyword 1>", "<keyword 2>", ...],
    "keywords_missing": ["<missing keyword 1>", "<missing keyword 2>", ...]
}}"""
            else:
                user_content = f"""Please analyze this resume:

RESUME:
{resume_text}

Provide analysis in JSON format with this structure:
{{
    "overall_score": <score 0-100>,
    "overall_assessment": "<brief overall assessment>",
    "strengths": ["<strength 1>", "<strength 2>", ...],
    "areas_for_improvement": ["<improvement 1>", "<improvement 2>", ...],
    "technical_skills": ["<skill 1>", "<skill 2>", ...],
    "soft_skills": ["<skill 1>", "<skill 2>", ...],
    "recommendations": ["<recommendation 1>", "<recommendation 2>", ...],
    "ats_suggestions": ["<suggestion 1>", "<suggestion 2>", ...]
}}"""
            
            messages = [{"role": "user", "content": user_content}]
            
            # Make API request
            response = await self._make_request(
                messages=messages,
                system_prompt=system_prompt,
                temperature=0.3,  # Lower temperature for consistent analysis
                max_tokens=2048
            )
            
            # Extract content from response
            if 'choices' not in response or not response['choices']:
                raise Exception("No response content received from AtlasCloud")
            
            content = response['choices'][0]['message']['content']
            
            # Try to parse as JSON
            try:
                analysis_data = json.loads(content)
            except json.JSONDecodeError:
                # If not valid JSON, create structured response
                analysis_data = {
                    "raw_analysis": content,
                    "parsing_error": "Response was not valid JSON"
                }
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return {
                "success": True,
                "analysis_data": analysis_data,
                "processing_time_ms": int(processing_time),
                "model_used": self.model,
                "timestamp": start_time.isoformat()
            }
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.error(f"Resume analysis failed: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "processing_time_ms": int(processing_time),
                "model_used": self.model,
                "timestamp": start_time.isoformat()
            }
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test the AtlasCloud API connection.
        
        Returns:
            Connection test results
        """
        try:
            messages = [{
                "role": "user",
                "content": "Please respond with exactly: 'AtlasCloud connection successful'"
            }]
            
            response = await self._make_request(
                messages=messages,
                system_prompt="You are a helpful assistant.",
                temperature=0.1,
                max_tokens=50,
                retries=1  # Single attempt for connection test
            )
            
            return {
                "success": True,
                "message": "AtlasCloud API connection successful",
                "model": self.model,
                "response": response
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": self.model
            }
    
    async def get_service_info(self) -> Dict[str, Any]:
        """
        Get service information and configuration.
        
        Returns:
            Service information dictionary
        """
        return {
            "service": "AtlasCloud AI Service",
            "model": self.model,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "api_key_configured": bool(self.api_key),
            "status": "ready"
        }


# Global service instance
_ai_service: Optional[AtlasCloudService] = None


async def get_ai_service() -> AtlasCloudService:
    """
    Get or create the global AI service instance.
    
    Returns:
        AtlasCloudService instance
    """
    global _ai_service
    
    if _ai_service is None:
        _ai_service = AtlasCloudService()
    
    return _ai_service


async def analyze_resume(resume_text: str, job_description: str = "") -> Dict[str, Any]:
    """
    Convenience function to analyze a resume.
    
    Args:
        resume_text: Resume content to analyze
        job_description: Optional job description for matching
        
    Returns:
        Analysis results dictionary
    """
    service = await get_ai_service()
    return await service.analyze_resume(resume_text, job_description)


async def test_ai_service() -> Dict[str, Any]:
    """
    Test the AI service connection.
    
    Returns:
        Test results dictionary
    """
    try:
        service = await get_ai_service()
        return await service.test_connection()
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def cleanup_ai_service():
    """Clean up the AI service resources."""
    global _ai_service
    
    if _ai_service:
        await _ai_service.close()
        _ai_service = None


# For testing when run directly
if __name__ == "__main__":
    async def main():
        print("Testing AtlasCloud AI Service...")
        result = await test_ai_service()
        print(json.dumps(result, indent=2))
        await cleanup_ai_service()
    
    asyncio.run(main())