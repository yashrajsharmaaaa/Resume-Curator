"""
Simplified keyword extraction module for Resume Curator application.

This module provides basic keyword extraction for SDE1 portfolio demonstration.
Focuses on essential functionality without over-engineering.
"""

import logging
import re
from typing import Dict, List, Set
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


class KeywordExtractor:
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
            basic_keywords = self._extract_basic_keywords(
                cleaned_text, min_keyword_length
            )
            
            # Extract phrases if enabled
            phrases = []
            if include_phrases:
                phrases = self._extract_phrases(cleaned_text)
            
            # Combine keywords and phrases
            all_candidates = basic_keywords + phrases
            
            # Calculate keyword frequencies
            keyword_frequencies = Counter(all_candidates)
            
            # Calculate importance scores
            importance_scores = await self._calculate_importance_scores(
                all_candidates, cleaned_text
            )
            
            # Categorize keywords
            categorized_keywords = self._categorize_keywords(all_candidates)
            
            # Select top keywords based on importance
            top_keywords = self._select_top_keywords(
                all_candidates, importance_scores, max_keywords
            )
            
            # Create result
            result = KeywordExtractionResult(
                technical_keywords=categorized_keywords['technical'],
                soft_skill_keywords=categorized_keywords['soft_skills'],
                industry_keywords=categorized_keywords['industry'],
                action_keywords=categorized_keywords['action'],
                certification_keywords=categorized_keywords['certification'],
                tool_keywords=categorized_keywords['tools'],
                all_keywords=top_keywords,
                keyword_frequencies=dict(keyword_frequencies),
                keyword_importance_scores=importance_scores,
                extraction_metadata={
                    'total_candidates': len(all_candidates),
                    'text_length': len(text),
                    'phrases_extracted': len(phrases),
                    'transformer_used': self.use_transformers
                }
            )
            
            logger.info(f"Keyword extraction completed. Found {len(top_keywords)} keywords")
            return result
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            raise
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for keyword extraction."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces and hyphens
        text = re.sub(r'[^\w\s\-]', ' ', text)
        
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove extra whitespace
        text = text.strip()
        
        return text
    
    def _extract_basic_keywords(self, text: str, min_length: int) -> List[str]:
        """Extract basic keywords using NLTK."""
        # Tokenize
        tokens = word_tokenize(text)
        
        # POS tagging
        pos_tags = pos_tag(tokens)
        
        # Filter for relevant POS tags (nouns, adjectives, verbs)
        relevant_pos = ['NN', 'NNS', 'NNP', 'NNPS', 'JJ', 'JJR', 'JJS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
        
        keywords = []
        for word, pos in pos_tags:
            if (pos in relevant_pos and 
                len(word) >= min_length and 
                word not in self.stop_words and
                word.isalpha()):
                
                # Lemmatize the word
                lemmatized = self.lemmatizer.lemmatize(word)
                keywords.append(lemmatized)
        
        return keywords
    
    def _extract_phrases(self, text: str) -> List[str]:
        """Extract meaningful phrases from text."""
        phrases = []
        
        # Extract noun phrases using chunking
        sentences = sent_tokenize(text)
        
        for sentence in sentences:
            tokens = word_tokenize(sentence)
            pos_tags = pos_tag(tokens)
            
            # Simple noun phrase extraction
            current_phrase = []
            for word, pos in pos_tags:
                if pos.startswith('NN') or pos.startswith('JJ'):
                    current_phrase.append(word)
                else:
                    if len(current_phrase) >= 2:
                        phrase = ' '.join(current_phrase)
                        if len(phrase) > 4:  # Minimum phrase length
                            phrases.append(phrase)
                    current_phrase = []
            
            # Don't forget the last phrase
            if len(current_phrase) >= 2:
                phrase = ' '.join(current_phrase)
                if len(phrase) > 4:
                    phrases.append(phrase)
        
        # Extract common technical phrases
        technical_patterns = [
            r'\b\w+\s+development\b',
            r'\b\w+\s+engineering\b',
            r'\b\w+\s+management\b',
            r'\b\w+\s+analysis\b',
            r'\b\w+\s+design\b',
            r'\bmachine\s+learning\b',
            r'\bdata\s+science\b',
            r'\bweb\s+development\b',
            r'\bproject\s+management\b'
        ]
        
        for pattern in technical_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            phrases.extend([match.lower() for match in matches])
        
        return list(set(phrases))  # Remove duplicates
    
    async def _calculate_importance_scores(
        self, 
        keywords: List[str], 
        text: str
    ) -> Dict[str, float]:
        """Calculate importance scores for keywords."""
        scores = {}
        
        # TF-IDF-like scoring
        total_words = len(text.split())
        
        for keyword in set(keywords):
            # Term frequency
            tf = keywords.count(keyword) / len(keywords)
            
            # Position scoring (keywords appearing early get higher scores)
            first_occurrence = text.find(keyword)
            position_score = 1.0 - (first_occurrence / len(text)) if first_occurrence != -1 else 0.5
            
            # Length bonus (longer keywords often more specific)
            length_bonus = min(len(keyword) / 10, 1.0)
            
            # Category bonus
            category_bonus = self._get_category_bonus(keyword)
            
            # Combine scores
            importance = (tf * 0.4 + position_score * 0.2 + 
                         length_bonus * 0.2 + category_bonus * 0.2)
            
            scores[keyword] = importance
        
        # Semantic similarity scoring if transformers available
        if self.use_transformers and self.sentence_model:
            try:
                semantic_scores = await self._calculate_semantic_scores(keywords, text)
                # Combine with existing scores
                for keyword in scores:
                    if keyword in semantic_scores:
                        scores[keyword] = (scores[keyword] * 0.7 + 
                                         semantic_scores[keyword] * 0.3)
            except Exception as e:
                logger.warning(f"Semantic scoring failed: {e}")
        
        return scores
    
    def _get_category_bonus(self, keyword: str) -> float:
        """Get bonus score based on keyword category."""
        keyword_lower = keyword.lower()
        
        # Check technical keywords
        for category, keywords in self.technical_keywords.items():
            if keyword_lower in keywords:
                return 0.8
        
        # Check soft skills
        if keyword_lower in self.soft_skills_keywords:
            return 0.6
        
        # Check industry keywords
        for category, keywords in self.industry_keywords.items():
            if keyword_lower in keywords:
                return 0.7
        
        # Check action keywords
        if keyword_lower in self.action_keywords:
            return 0.5
        
        # Check certification keywords
        if any(cert in keyword_lower for cert in self.certification_keywords):
            return 0.9
        
        return 0.3  # Default bonus
    
    async def _calculate_semantic_scores(
        self, 
        keywords: List[str], 
        text: str
    ) -> Dict[str, float]:
        """Calculate semantic importance scores using transformers."""
        if not self.sentence_model:
            return {}
        
        try:
            # Get embeddings for keywords and text
            keyword_embeddings = self.sentence_model.encode(keywords)
            text_embedding = self.sentence_model.encode([text])
            
            # Calculate similarity scores
            similarities = np.dot(keyword_embeddings, text_embedding.T).flatten()
            
            # Normalize scores
            max_sim = np.max(similarities) if len(similarities) > 0 else 1.0
            normalized_scores = similarities / max_sim if max_sim > 0 else similarities
            
            return dict(zip(keywords, normalized_scores))
            
        except Exception as e:
            logger.warning(f"Semantic scoring calculation failed: {e}")
            return {}
    
    def _categorize_keywords(self, keywords: List[str]) -> Dict[str, List[str]]:
        """Categorize keywords into different types."""
        categorized = {
            'technical': [],
            'soft_skills': [],
            'industry': [],
            'action': [],
            'certification': [],
            'tools': []
        }
        
        for keyword in set(keywords):
            keyword_lower = keyword.lower()
            
            # Technical keywords
            for category, tech_keywords in self.technical_keywords.items():
                if keyword_lower in tech_keywords:
                    categorized['technical'].append(keyword)
                    break
            
            # Soft skills
            if keyword_lower in self.soft_skills_keywords:
                categorized['soft_skills'].append(keyword)
            
            # Industry keywords
            for category, industry_keywords in self.industry_keywords.items():
                if keyword_lower in industry_keywords:
                    categorized['industry'].append(keyword)
                    break
            
            # Action keywords
            if keyword_lower in self.action_keywords:
                categorized['action'].append(keyword)
            
            # Certification keywords
            if any(cert in keyword_lower for cert in self.certification_keywords):
                categorized['certification'].append(keyword)
            
            # Tools (subset of technical)
            if keyword_lower in self.technical_keywords.get('tools', []):
                categorized['tools'].append(keyword)
        
        return categorized
    
    def _select_top_keywords(
        self, 
        keywords: List[str], 
        scores: Dict[str, float], 
        max_keywords: int
    ) -> List[str]:
        """Select top keywords based on importance scores."""
        # Sort keywords by score
        sorted_keywords = sorted(
            set(keywords), 
            key=lambda k: scores.get(k, 0), 
            reverse=True
        )
        
        return sorted_keywords[:max_keywords]
    
    def extract_job_keywords(self, job_description: str) -> KeywordExtractionResult:
        """
        Extract keywords specifically from job descriptions.
        
        Args:
            job_description: Job description text
            
        Returns:
            KeywordExtractionResult optimized for job requirements
        """
        # Use async method synchronously for job descriptions
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.extract_keywords(
                job_description,
                max_keywords=30,  # Fewer keywords for job descriptions
                include_phrases=True
            )
        )
    
    def compare_keywords(
        self, 
        resume_keywords: KeywordExtractionResult,
        job_keywords: KeywordExtractionResult
    ) -> Dict[str, any]:
        """
        Compare keywords between resume and job description.
        
        Args:
            resume_keywords: Keywords extracted from resume
            job_keywords: Keywords extracted from job description
            
        Returns:
            Dictionary with comparison results
        """
        resume_set = set(kw.lower() for kw in resume_keywords.all_keywords)
        job_set = set(kw.lower() for kw in job_keywords.all_keywords)
        
        matching_keywords = resume_set.intersection(job_set)
        missing_keywords = job_set - resume_set
        extra_keywords = resume_set - job_set
        
        # Calculate match percentage
        match_percentage = len(matching_keywords) / len(job_set) * 100 if job_set else 0
        
        return {
            'matching_keywords': list(matching_keywords),
            'missing_keywords': list(missing_keywords),
            'extra_keywords': list(extra_keywords),
            'match_percentage': match_percentage,
            'total_job_keywords': len(job_set),
            'total_resume_keywords': len(resume_set),
            'matching_count': len(matching_keywords)
        }