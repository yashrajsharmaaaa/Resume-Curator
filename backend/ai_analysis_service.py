

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
    
    def __init__(self):
        self.api_key = os.getenv('ATLASCLOUD_API_KEY')
        self.base_url = os.getenv('ATLASCLOUD_BASE_URL', 'https://api.atlascloud.ai/v1')
        self.model = os.getenv('ATLASCLOUD_MODEL', 'openai/gpt-oss-20b')
        self.timeout = int(os.getenv('ATLASCLOUD_TIMEOUT', '30'))
        
        if not self.api_key:
            raise ValueError("ATLASCLOUD_API_KEY environment variable is required")
        
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        logger.info(f"AtlasCloud service initialized with model: {self.model}")
    

    
    async def _make_request(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": messages,
            "systemPrompt": system_prompt,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"AtlasCloud API error: {e}")
            raise Exception(f"AtlasCloud API failed: {str(e)}")
    
    async def analyze_resume(
        self,
        resume_text: str,
        job_description: str = ""
    ) -> Dict[str, Any]:
        try:
            system_prompt = """You are an expert resume analyzer and career consultant. 
            Analyze the resume and provide detailed feedback in a structured format. 
            Focus on practical, actionable insights that will help improve the resume."""
            
            # Different analysis based on whether job description is provided
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
            
            response = await self._make_request(
                messages=messages,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=1000
            )
            
            if 'choices' not in response or not response['choices']:
                raise Exception("No response content received from AtlasCloud")
            
            content = response['choices'][0]['message']['content']
            
            # Parse JSON response with fallback handling
            try:
                analysis_data = json.loads(content)
            except json.JSONDecodeError:
                analysis_data = {
                    "raw_analysis": content,
                    "parsing_error": "Response was not valid JSON"
                }
            
            return {
                "success": True,
                "analysis_data": analysis_data,
                "model_used": self.model
            }
            
        except Exception as e:
            logger.error(f"Resume analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "model_used": self.model
            }
    
    async def test_connection(self) -> Dict[str, Any]:
        try:
            messages = [{
                "role": "user",
                "content": "Say 'Connection successful'"
            }]
            
            response = await self._make_request(
                messages=messages,
                system_prompt="You are a helpful assistant.",
                temperature=0.1,
                max_tokens=10
            )
            
            return {
                "success": True,
                "message": "AtlasCloud API connection successful",
                "model": self.model
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": self.model
            }
    
    async def get_service_info(self) -> Dict[str, Any]:
        return {
            "service": "AtlasCloud AI Service",
            "model": self.model,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "api_key_configured": bool(self.api_key),
            "status": "ready"
        }


_ai_service: Optional[AtlasCloudService] = None


async def get_ai_service() -> AtlasCloudService:
    global _ai_service
    
    if _ai_service is None:
        _ai_service = AtlasCloudService()
    
    return _ai_service


async def analyze_resume(resume_text: str, job_description: str = "") -> Dict[str, Any]:
    service = await get_ai_service()
    return await service.analyze_resume(resume_text, job_description)


async def test_ai_service() -> Dict[str, Any]:
    try:
        service = await get_ai_service()
        return await service.test_connection()
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def cleanup_ai_service():
    global _ai_service
    
    if _ai_service:
        await _ai_service.close()
        _ai_service = None


if __name__ == "__main__":
    async def main():
        print("Testing AtlasCloud AI Service...")
        result = await test_ai_service()
        print(json.dumps(result, indent=2))
        await cleanup_ai_service()
    
    asyncio.run(main())