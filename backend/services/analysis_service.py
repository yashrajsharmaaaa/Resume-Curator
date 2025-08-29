"""
Analysis service for Resume Curator application.

This module provides the core analysis service that orchestrates all AI and NLP
components for comprehensive resume analysis as required by Requirements 3.1, 10.2, 10.4.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import asyncio

from ai_analysis import (
    CompatibilityScoringAlgorithm,
    RecommendationGenerator,
    SkillsAnalyzer,
    OpenAIClient,
    DetailedScore,
    RecommendationSet,
    SkillsAnalysisResult
)
from nlp_processing import (
    KeywordExtractor, 
    SkillCategorizer,
    KeywordExtractionResult,
    SkillCategorizationResult
)

# Configure logging
logger = logging.getLogger(__name__)


class AnalysisConfiguration:
    """Configuration for analysis processing."""
    
    def __init__(
        self,
        use_ai_enhancement: bool = True,
        use_transformers: bool = True,
        use_semantic_analysis: bool = True,
        max_keywords: int = 50,
        confidence_threshold: float = 0.6,
        enable_caching: bool = True
    ):
        self.use_ai_enhancement = use_ai_enhancement
        self.use_transformers = use_transformers
        self.use_semantic_analysis = use_semantic_analysis
        self.max_keywords = max_keywords
        self.confidence_threshold = confidence_threshold
        self.enable_caching = enable_caching


class AnalysisResult:
    """Complete analysis result container."""
    
    def __init__(
        self,
        analysis_id: str,
        compatibility_score: DetailedScore,
        recommendations: RecommendationSet,
        skills_analysis: SkillsAnalysisResult,
        keyword_analysis: KeywordExtractionResult,
        skill_categorization: SkillCategorizationResult,
        processing_metadata: Dict[str, Any]
    ):
        self.analysis_id = analysis_id
        self.compatibility_score = compatibility_score
        self.recommendations = recommendations
        self.skills_analysis = skills_analysis
        self.keyword_analysis = keyword_analysis
        self.skill_categorization = skill_categorization
        self.processing_metadata = processing_metadata
        self.completed_at = datetime.utcnow()


class AnalysisService:
    """
    Core analysis service that orchestrates all AI and NLP components.
    
    Provides comprehensive resume analysis with progress tracking,
    error handling, and performance optimization.
    """
    
    def __init__(self, config: Optional[AnalysisConfiguration] = None):
        """
        Initialize analysis service.
        
        Args:
            config: Analysis configuration options
        """
        self.config = config or AnalysisConfiguration()
        
        # Initialize components
        self.openai_client = OpenAIClient()
        self.scoring_algorithm = CompatibilityScoringAlgorithm(
            openai_client=self.openai_client,
            use_ai_enhancement=self.config.use_ai_enhancement
        )
        self.recommendation_generator = RecommendationGenerator(
            openai_client=self.openai_client
        )
        self.skills_analyzer = SkillsAnalyzer(self.openai_client)
        self.keyword_extractor = KeywordExtractor(
            use_transformers=self.config.use_transformers
        )
        self.skill_categorizer = SkillCategorizer(
            use_semantic_analysis=self.config.use_semantic_analysis
        )
        
        # Cache for repeated analyses (simple in-memory cache)
        self._cache: Dict[str, Any] = {}
        
        logger.info("AnalysisService initialized")
    
    async def analyze_resume(
        self,
        resume_text: str,
        job_description: str,
        analysis_id: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> AnalysisResult:
        """
        Perform comprehensive resume analysis.
        
        Args:
            resume_text: Resume text content
            job_description: Job description text
            analysis_id: Optional analysis identifier
            progress_callback: Optional callback for progress updates
            
        Returns:
            AnalysisResult with comprehensive analysis data
            
        Raises:
            ValueError: If input validation fails
            Exception: If analysis fails
        """
        try:
            start_time = datetime.utcnow()
            analysis_id = analysis_id or str(uuid.uuid4())
            
            logger.info(f"Starting comprehensive analysis {analysis_id}")
            
            # Validate inputs
            self._validate_inputs(resume_text, job_description)
            
            # Check cache if enabled
            cache_key = self._generate_cache_key(resume_text, job_description)
            if self.config.enable_caching and cache_key in self._cache:
                logger.info(f"Returning cached result for analysis {analysis_id}")
                cached_result = self._cache[cache_key]
                cached_result.analysis_id = analysis_id  # Update ID
                return cached_result
            
            # Progress tracking
            total_steps = 5
            current_step = 0
            
            def update_progress(step_name: str, percentage: int):
                nonlocal current_step
                current_step += 1
                if progress_callback:
                    progress_callback(analysis_id, step_name, percentage, current_step, total_steps)
            
            # Step 1: Skills Analysis
            update_progress("Analyzing skills and experience", 20)
            skills_analysis = await self.skills_analyzer.analyze_skills(resume_text)
            
            # Step 2: Keyword Extraction and Analysis
            update_progress("Extracting and analyzing keywords", 40)
            resume_keywords = await self.keyword_extractor.extract_keywords(
                resume_text, 
                max_keywords=self.config.max_keywords
            )
            job_keywords = self.keyword_extractor.extract_job_keywords(job_description)
            keyword_comparison = self.keyword_extractor.compare_keywords(
                resume_keywords, job_keywords
            )
            
            # Step 3: Skill Categorization
            update_progress("Categorizing skills", 60)
            all_skills = (
                skills_analysis.technical_skills + 
                skills_analysis.soft_skills + 
                skills_analysis.tools_and_software
            )
            skill_categorization = await self.skill_categorizer.categorize_skills(
                all_skills,
                confidence_threshold=self.config.confidence_threshold
            )
            
            # Step 4: Compatibility Scoring
            update_progress("Calculating compatibility score", 80)
            compatibility_score = await self.scoring_algorithm.calculate_compatibility_score(
                resume_text=resume_text,
                job_description=job_description
            )
            
            # Step 5: Generate Recommendations
            update_progress("Generating recommendations", 95)
            recommendations = await self.recommendation_generator.generate_recommendations(
                resume_text=resume_text,
                job_description=job_description,
                skills_analysis=skills_analysis,
                keyword_analysis=resume_keywords,
                skill_categorization=skill_categorization
            )
            
            # Complete analysis
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds() * 1000
            
            # Create processing metadata
            processing_metadata = {
                "analysis_id": analysis_id,
                "processing_time_ms": processing_time,
                "configuration": {
                    "ai_enhanced": self.config.use_ai_enhancement,
                    "transformers_used": self.config.use_transformers,
                    "semantic_analysis_used": self.config.use_semantic_analysis,
                    "max_keywords": self.config.max_keywords,
                    "confidence_threshold": self.config.confidence_threshold
                },
                "component_stats": {
                    "skills_analysis": {
                        "technical_skills_count": len(skills_analysis.technical_skills),
                        "soft_skills_count": len(skills_analysis.soft_skills),
                        "certifications_count": len(skills_analysis.certifications),
                        "tools_count": len(skills_analysis.tools_and_software)
                    },
                    "keyword_analysis": {
                        "resume_keywords_count": len(resume_keywords.all_keywords),
                        "job_keywords_count": len(job_keywords.all_keywords),
                        "match_percentage": keyword_comparison["match_percentage"],
                        "missing_keywords_count": len(keyword_comparison["missing_keywords"])
                    },
                    "skill_categorization": {
                        "categorization_confidence": skill_categorization.categorization_confidence,
                        "categorized_skills_count": sum(len(getattr(skill_categorization, attr).skills) 
                                                      for attr in ['technical_skills', 'soft_skills', 'domain_skills', 
                                                                  'tools_and_platforms', 'certifications', 'languages', 'methodologies']),
                        "uncategorized_count": len(skill_categorization.uncategorized_skills)
                    },
                    "recommendations": {
                        "total_recommendations": len(recommendations.recommendations),
                        "high_priority_count": len(recommendations.priority_recommendations),
                        "quick_wins_count": len(recommendations.quick_wins),
                        "total_impact_score": recommendations.total_impact_score
                    }
                },
                "performance_metrics": {
                    "cache_hit": False,
                    "processing_steps": total_steps,
                    "started_at": start_time.isoformat(),
                    "completed_at": end_time.isoformat()
                }
            }
            
            # Create result
            result = AnalysisResult(
                analysis_id=analysis_id,
                compatibility_score=compatibility_score,
                recommendations=recommendations,
                skills_analysis=skills_analysis,
                keyword_analysis=resume_keywords,
                skill_categorization=skill_categorization,
                processing_metadata=processing_metadata
            )
            
            # Cache result if enabled
            if self.config.enable_caching:
                self._cache[cache_key] = result
                # Simple cache cleanup - keep only last 100 results
                if len(self._cache) > 100:
                    oldest_key = next(iter(self._cache))
                    del self._cache[oldest_key]
            
            # Final progress update
            update_progress("Analysis completed", 100)
            
            logger.info(f"Analysis {analysis_id} completed successfully in {processing_time:.1f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Analysis {analysis_id} failed: {e}")
            raise
    
    def _validate_inputs(self, resume_text: str, job_description: str) -> None:
        """
        Validate analysis inputs.
        
        Args:
            resume_text: Resume text to validate
            job_description: Job description text to validate
            
        Raises:
            ValueError: If validation fails
        """
        if not resume_text or not resume_text.strip():
            raise ValueError("Resume text cannot be empty")
        
        if not job_description or not job_description.strip():
            raise ValueError("Job description cannot be empty")
        
        if len(resume_text.strip()) < 50:
            raise ValueError("Resume text is too short (minimum 50 characters)")
        
        if len(job_description.strip()) < 50:
            raise ValueError("Job description is too short (minimum 50 characters)")
        
        if len(resume_text) > 50000:
            raise ValueError("Resume text is too long (maximum 50,000 characters)")
        
        if len(job_description) > 10000:
            raise ValueError("Job description is too long (maximum 10,000 characters)")
    
    def _generate_cache_key(self, resume_text: str, job_description: str) -> str:
        """
        Generate cache key for analysis inputs.
        
        Args:
            resume_text: Resume text
            job_description: Job description text
            
        Returns:
            Cache key string
        """
        import hashlib
        
        # Create hash of inputs and configuration
        content = f"{resume_text.strip()}{job_description.strip()}"
        config_str = f"{self.config.use_ai_enhancement}{self.config.use_transformers}{self.config.use_semantic_analysis}"
        
        return hashlib.md5(f"{content}{config_str}".encode()).hexdigest()
    
    async def get_analysis_summary(self, result: AnalysisResult) -> Dict[str, Any]:
        """
        Get a summary of analysis results.
        
        Args:
            result: Analysis result to summarize
            
        Returns:
            Dictionary with analysis summary
        """
        return {
            "analysis_id": result.analysis_id,
            "overall_compatibility_score": result.compatibility_score.overall_score,
            "confidence_level": result.compatibility_score.confidence_level,
            "top_recommendations": [
                {
                    "title": rec.title,
                    "priority": rec.priority.value,
                    "impact_score": rec.impact_score,
                    "effort_level": rec.effort_level
                }
                for rec in result.recommendations.recommendations[:5]
            ],
            "skills_summary": {
                "technical_skills": len(result.skills_analysis.technical_skills),
                "soft_skills": len(result.skills_analysis.soft_skills),
                "certifications": len(result.skills_analysis.certifications)
            },
            "keyword_match_percentage": result.processing_metadata["component_stats"]["keyword_analysis"]["match_percentage"],
            "processing_time_ms": result.processing_metadata["processing_time_ms"],
            "completed_at": result.completed_at.isoformat()
        }
    
    def clear_cache(self) -> int:
        """
        Clear analysis cache.
        
        Returns:
            Number of cached items cleared
        """
        cache_size = len(self._cache)
        self._cache.clear()
        logger.info(f"Cleared {cache_size} cached analysis results")
        return cache_size
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            "cached_analyses": len(self._cache),
            "cache_enabled": self.config.enable_caching,
            "cache_hit_rate": "Not tracked in simple implementation"
        }