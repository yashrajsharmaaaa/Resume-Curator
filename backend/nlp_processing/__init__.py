"""
NLP processing module for Resume Curator application.

This module provides advanced NLP capabilities including text similarity,
embeddings, keyword extraction, and skill categorization using modern
NLP techniques as required by Requirements 4.2, 4.5, 6.2.
"""

from .text_similarity import TextSimilarityAnalyzer, SimilarityResult
from .keyword_extractor import KeywordExtractor, KeywordExtractionResult
from .skill_categorizer import SkillCategorizer, SkillCategorizationResult, SkillCategory

__all__ = [
    "TextSimilarityAnalyzer",
    "SimilarityResult", 
    "KeywordExtractor",
    "KeywordExtractionResult",
    "SkillCategorizer",
    "SkillCategorizationResult",
    "SkillCategory"
]