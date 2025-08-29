"""
Message translation system for Resume Curator backend.

Provides user-friendly error message translation for different languages
while maintaining security and consistency.
"""

import json
import logging
from typing import Dict, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class MessageTranslator:
    """
    Message translator for error messages and user-facing text.
    """
    
    def __init__(self, translations_dir: str = "translations"):
        self.translations_dir = Path(translations_dir)
        self.translations: Dict[str, Dict[str, str]] = {}
        self.default_language = 'en'
        self.supported_languages = {'en', 'es', 'fr', 'de', 'it', 'pt', 'zh', 'ja', 'ko'}
        
        # Load translations
        self._load_translations()
    
    def _load_translations(self) -> None:
        """Load translation files from the translations directory."""
        try:
            # Create translations directory if it doesn't exist
            self.translations_dir.mkdir(parents=True, exist_ok=True)
            
            # Load each supported language
            for language in self.supported_languages:
                translation_file = self.translations_dir / f"{language}.json"
                
                if translation_file.exists():
                    try:
                        with open(translation_file, 'r', encoding='utf-8') as f:
                            self.translations[language] = json.load(f)
                        logger.info(f"Loaded translations for language: {language}")
                    except Exception as e:
                        logger.warning(f"Failed to load translations for {language}: {e}")
                        self.translations[language] = {}
                else:
                    # Create default translation file for English
                    if language == 'en':
                        self._create_default_english_translations(translation_file)
                    else:
                        self.translations[language] = {}
            
            logger.info(f"Translation system initialized with {len(self.translations)} languages")
            
        except Exception as e:
            logger.error(f"Failed to initialize translation system: {e}")
            # Fallback to empty translations
            self.translations = {lang: {} for lang in self.supported_languages}
    
    def _create_default_english_translations(self, file_path: Path) -> None:
        """Create default English translation file."""
        try:
            default_translations = {
                # Common error messages
                "validation_failed": "The request contains invalid data. Please check your input and try again.",
                "file_too_large": "The file is too large. Please use a file smaller than the maximum size limit.",
                "file_invalid_type": "The file type is not supported. Please use a PDF, DOC, or DOCX file.",
                "rate_limit_exceeded": "You've made too many requests. Please wait before trying again.",
                "ai_service_unavailable": "The AI analysis service is temporarily unavailable. Please try again later.",
                "internal_server_error": "An internal server error occurred. Please try again.",
                
                # Field validation messages
                "field_required": "This field is required.",
                "field_too_short": "This field is too short.",
                "field_too_long": "This field is too long.",
                "invalid_email": "Please enter a valid email address.",
                "invalid_phone": "Please enter a valid phone number.",
                "invalid_date": "Please enter a valid date.",
                
                # File processing messages
                "file_processing_failed": "We couldn't process your file. Please try again or use a different file.",
                "file_corrupted": "The file appears to be corrupted. Please try uploading a different file.",
                "file_not_found": "The requested file was not found.",
                
                # Analysis messages
                "analysis_failed": "The analysis could not be completed. Please try again.",
                "analysis_in_progress": "An analysis is already in progress. Please wait for it to complete.",
                "analysis_not_found": "The requested analysis was not found.",
                "insufficient_content": "There isn't enough content to perform a meaningful analysis.",
                
                # Security messages
                "security_violation": "Your request was blocked for security reasons.",
                "suspicious_activity": "Suspicious activity detected. Your request has been blocked.",
                "malicious_content": "Potentially malicious content was detected in your request.",
                
                # Success messages
                "upload_successful": "File uploaded successfully.",
                "analysis_started": "Analysis started successfully.",
                "analysis_completed": "Analysis completed successfully.",
                
                # Suggestions
                "suggestion_compress_file": "Compress your file to reduce its size",
                "suggestion_use_pdf": "Use a PDF instead of a Word document for smaller file size",
                "suggestion_wait_retry": "Wait a few minutes before making another request",
                "suggestion_contact_support": "Contact support if the problem persists",
                "suggestion_check_format": "Make sure your file has the correct extension (.pdf, .doc, .docx)",
                "suggestion_provide_details": "Provide more detailed information in the required fields",
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_translations, f, indent=2, ensure_ascii=False)
            
            self.translations['en'] = default_translations
            logger.info("Created default English translation file")
            
        except Exception as e:
            logger.error(f"Failed to create default English translations: {e}")
            self.translations['en'] = {}
    
    async def translate_message(
        self,
        message: str,
        target_language: str = 'en',
        message_key: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Translate a message to the target language.
        
        Args:
            message: The message to translate
            target_language: Target language code
            message_key: Optional message key for direct lookup
            context: Optional context for parameterized messages
            
        Returns:
            Translated message or original message if translation not available
        """
        try:
            # Normalize language code
            target_language = self._normalize_language_code(target_language)
            
            # If target language is not supported, use default
            if target_language not in self.supported_languages:
                target_language = self.default_language
            
            # Get translations for target language
            language_translations = self.translations.get(target_language, {})
            
            # Try direct key lookup first
            if message_key and message_key in language_translations:
                translated = language_translations[message_key]
                return self._apply_context(translated, context)
            
            # Try to find translation by message content
            translated = self._find_translation_by_content(message, language_translations)
            if translated:
                return self._apply_context(translated, context)
            
            # Try fuzzy matching for common error patterns
            translated = self._fuzzy_match_translation(message, language_translations)
            if translated:
                return self._apply_context(translated, context)
            
            # If no translation found and not default language, try default language
            if target_language != self.default_language:
                return await self.translate_message(message, self.default_language, message_key, context)
            
            # Return original message if no translation available
            return message
            
        except Exception as e:
            logger.warning(f"Translation failed for message '{message}' to '{target_language}': {e}")
            return message
    
    def _normalize_language_code(self, language_code: str) -> str:
        """Normalize language code to supported format."""
        if not language_code:
            return self.default_language
        
        # Extract primary language (e.g., 'en-US' -> 'en')
        primary_language = language_code.lower().split('-')[0].split('_')[0]
        
        # Map some common variations
        language_mapping = {
            'zh-cn': 'zh',
            'zh-tw': 'zh',
            'pt-br': 'pt',
            'pt-pt': 'pt',
        }
        
        full_code = language_code.lower()
        if full_code in language_mapping:
            return language_mapping[full_code]
        
        return primary_language if primary_language in self.supported_languages else self.default_language
    
    def _find_translation_by_content(self, message: str, translations: Dict[str, str]) -> Optional[str]:
        """Find translation by matching message content."""
        # Direct match
        for key, translation in translations.items():
            if message.lower() == translation.lower():
                return translation
        
        return None
    
    def _fuzzy_match_translation(self, message: str, translations: Dict[str, str]) -> Optional[str]:
        """Find translation using fuzzy matching for common patterns."""
        message_lower = message.lower()
        
        # Define pattern mappings
        pattern_mappings = {
            'file.*too.*large': ['file_too_large', 'file_size_exceeded'],
            'file.*type.*not.*supported': ['file_invalid_type', 'unsupported_file_type'],
            'rate.*limit.*exceeded': ['rate_limit_exceeded', 'too_many_requests'],
            'validation.*failed': ['validation_failed', 'invalid_input'],
            'analysis.*failed': ['analysis_failed', 'analysis_error'],
            'service.*unavailable': ['service_unavailable', 'ai_service_unavailable'],
            'internal.*server.*error': ['internal_server_error', 'server_error'],
            'file.*not.*found': ['file_not_found', 'resource_not_found'],
            'permission.*denied': ['permission_denied', 'access_denied'],
            'security.*violation': ['security_violation', 'blocked_request'],
        }
        
        import re
        
        for pattern, possible_keys in pattern_mappings.items():
            if re.search(pattern, message_lower):
                for key in possible_keys:
                    if key in translations:
                        return translations[key]
        
        return None
    
    def _apply_context(self, message: str, context: Optional[Dict[str, Any]]) -> str:
        """Apply context variables to a translated message."""
        if not context:
            return message
        
        try:
            # Simple string formatting with context variables
            return message.format(**context)
        except (KeyError, ValueError) as e:
            logger.warning(f"Failed to apply context to message '{message}': {e}")
            return message
    
    def get_supported_languages(self) -> list:
        """Get list of supported language codes."""
        return list(self.supported_languages)
    
    def is_language_supported(self, language_code: str) -> bool:
        """Check if a language is supported."""
        normalized = self._normalize_language_code(language_code)
        return normalized in self.supported_languages
    
    def get_translation_coverage(self, language_code: str) -> Dict[str, Any]:
        """Get translation coverage statistics for a language."""
        try:
            normalized = self._normalize_language_code(language_code)
            
            if normalized not in self.translations:
                return {'language': normalized, 'coverage': 0, 'total_keys': 0, 'translated_keys': 0}
            
            language_translations = self.translations[normalized]
            english_translations = self.translations.get('en', {})
            
            total_keys = len(english_translations)
            translated_keys = len([k for k in english_translations.keys() if k in language_translations])
            coverage = (translated_keys / total_keys * 100) if total_keys > 0 else 0
            
            return {
                'language': normalized,
                'coverage': round(coverage, 2),
                'total_keys': total_keys,
                'translated_keys': translated_keys,
                'missing_keys': [k for k in english_translations.keys() if k not in language_translations]
            }
            
        except Exception as e:
            logger.error(f"Failed to get translation coverage for {language_code}: {e}")
            return {'language': language_code, 'coverage': 0, 'total_keys': 0, 'translated_keys': 0}


# Global message translator instance
message_translator = MessageTranslator()


async def translate_error_message(
    message: str,
    target_language: str = 'en',
    message_key: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Convenience function to translate an error message.
    
    Args:
        message: The message to translate
        target_language: Target language code
        message_key: Optional message key for direct lookup
        context: Optional context for parameterized messages
        
    Returns:
        Translated message or original message if translation not available
    """
    return await message_translator.translate_message(
        message=message,
        target_language=target_language,
        message_key=message_key,
        context=context
    )


def get_supported_languages() -> list:
    """Get list of supported language codes."""
    return message_translator.get_supported_languages()


def is_language_supported(language_code: str) -> bool:
    """Check if a language is supported."""
    return message_translator.is_language_supported(language_code)