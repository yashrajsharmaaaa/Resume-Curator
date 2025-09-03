

import os
import json
import logging
from typing import Dict, Any
import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class SimpleAtlasCloudService:
    
    def __init__(self):
        self.api_key = os.getenv('ATLASCLOUD_API_KEY')
        self.base_url = os.getenv('ATLASCLOUD_BASE_URL', 'https://api.atlascloud.ai/v1')
        self.model = os.getenv('ATLASCLOUD_MODEL', 'openai/gpt-oss-20b')
        
        if not self.api_key:
            raise ValueError("ATLASCLOUD_API_KEY is required")
    
    async def analyze_resume(self, resume_text: str, job_description: str = "") -> Dict[str, Any]:
        try:
            if job_description:
                prompt = f"""
                Analyze this resume against the job description and provide feedback in JSON format:
                
                RESUME: {resume_text}
                JOB DESCRIPTION: {job_description}
                
                Return JSON with:
                - compatibility_score (0-100)
                - strengths (array of strings)
                - improvements (array of strings)
                - missing_skills (array of strings)
                """
            else:
                prompt = f"""
                Analyze this resume and provide feedback in JSON format:
                
                RESUME: {resume_text}
                
                Return JSON with:
                - overall_score (0-100)
                - strengths (array of strings)
                - improvements (array of strings)
                - skills_found (array of strings)
                """
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "max_tokens": 1000
                    }
                )
                
                if response.status_code != 200:
                    return {"error": f"API error: {response.status_code}"}
                
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Parse JSON with fallback
                try:
                    return {"success": True, "analysis": json.loads(content)}
                except json.JSONDecodeError:
                    return {"success": True, "analysis": {"raw_response": content}}
                    
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_connection(self) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": "Say 'Connection successful'"}],
                        "max_tokens": 10
                    }
                )
                return {"success": response.status_code == 200}
        except Exception as e:
            return {"success": False, "error": str(e)}


_ai_service = None

async def get_ai_service():
    global _ai_service
    if _ai_service is None:
        _ai_service = SimpleAtlasCloudService()
    return _ai_service

async def analyze_resume_simple(resume_text: str, job_description: str = "") -> Dict[str, Any]:
    service = await get_ai_service()
    return await service.analyze_resume(resume_text, job_description)