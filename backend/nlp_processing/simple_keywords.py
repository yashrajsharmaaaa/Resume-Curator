"""
Simplified keyword extraction module for Resume Curator application.

This module provides basic keyword extraction for SDE1 portfolio demonstration.
Focuses on essential functionality without over-engineering.
"""

import logging
import re
from typing import Dict, List
from collections import Counter

# Configure logging
logger = logging.getLogger(__name__)

# Common stop words to filter out
STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
    'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
    'above', 'below', 'between', 'among', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
}


class KeywordExtractionResult:
    """Simple result of keyword extraction analysis."""
    def __init__(self, keywords: List[str], frequencies: Dict[str, int]):
        self.keywords = keywords
        self.frequencies = frequencies


class SimpleKeywordExtractor:
    """
    Simple keyword extraction for SDE1 portfolio demonstration.
    
    Provides basic keyword extraction with frequency analysis.
    """
    
    def __init__(self):
        """Initialize simple keyword extractor."""
        # Technical skills keywords for matching
        self.tech_keywords = {
            'python', 'java', 'javascript', 'react', 'fastapi', 'postgresql',
            'docker', 'aws', 'git', 'sql', 'html', 'css', 'nodejs', 'api',
            'database', 'backend', 'frontend', 'web', 'development', 'software'
        }
        logger.info("Simple KeywordExtractor initialized")
    
    def extract_keywords(self, text: str, max_keywords: int = 20) -> KeywordExtractionResult:
        """Extract keywords from text using simple frequency analysis."""
        try:
            # Clean and normalize text
            cleaned_text = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
            words = cleaned_text.split()
            
            # Filter out stop words and short words
            filtered_words = [
                word for word in words 
                if word not in STOP_WORDS and len(word) > 2
            ]
            
            # Count word frequencies
            word_freq = Counter(filtered_words)
            
            # Get top keywords
            top_keywords = [word for word, _ in word_freq.most_common(max_keywords)]
            
            # Identify technical keywords
            tech_matches = [word for word in top_keywords if word in self.tech_keywords]
            
            logger.info(f"Extracted {len(top_keywords)} keywords, {len(tech_matches)} technical")
            
            return KeywordExtractionResult(
                keywords=top_keywords,
                frequencies=dict(word_freq)
            )
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return KeywordExtractionResult(keywords=[], frequencies={})
