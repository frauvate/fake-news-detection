"""
Text preprocessing and cleaning utilities for NLP pipeline
Optimized for Turkish news articles and similarity search
"""
import re
import html
import unicodedata
from typing import List, Optional, Set, Tuple
import logging

from backend.app.core.constants import *
from backend.app.core.exceptions import *

logger = logging.getLogger(__name__)


class TextProcessor:
    """
    Text processing and cleaning for NLP pipeline
    
    Optimized for Turkish news articles with focus on:
    - Preserving Turkish characters (çÇğĞıİöÖşŞüÜ)
    - Preserving numbers (important for news: dates, statistics)
    - Preparing text for embedding generation
    - Maintaining semantic meaning
    """
    
    def __init__(self, language: str = "tr"):
        """
        Initialize text processor
        
        Args:
            language: Language code (default: 'tr' for Turkish)
        """
        self.language = language
        self.stop_words = TURKISH_STOP_WORDS
        
        # Compile regex patterns for performance
        self._html_tag_pattern = re.compile(r'<[^>]+>')
        self._html_comment_pattern = re.compile(r'<!--.*?-->', re.DOTALL)
        self._script_pattern = re.compile(r'<script[^>]*>.*?</script>', re.DOTALL | re.IGNORECASE)
        self._style_pattern = re.compile(r'<style[^>]*>.*?</style>', re.DOTALL | re.IGNORECASE)
        
        self._url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        self._email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
        
        # Multiple spaces/newlines
        self._multiple_spaces = re.compile(r' +')
        self._multiple_newlines = re.compile(r'\n+')
        self._multiple_tabs = re.compile(r'\t+')
        
        # Special characters - PRESERVE Turkish letters and numbers
        # Only remove problematic characters
        self._problematic_chars = re.compile(r'[^\w\s\.,!?;:\-—–\(\)\"\'çÇğĞıİöÖşŞüÜ]', re.UNICODE)
        
        logger.info(f"TextProcessor initialized for language: {language}")
    
    def clean_for_embedding(
        self,
        text: str,
        *,
        remove_html: bool = True,
        remove_urls: bool = True,
        remove_emails: bool = True,
        remove_extra_whitespace: bool = True,
        lowercase: bool = True,
        validate_length: bool = True,
    ) -> str:
        """
        Clean text for embedding generation
        
        This is the MAIN method for preparing text for similarity search.
        Preserves:
        - Turkish characters (çÇğĞıİöÖşŞüÜ)
        - Numbers (important for dates, statistics, etc.)
        - Basic punctuation (.,!?;:)
        
        Args:
            text: Input text to clean
            remove_html: Remove HTML tags
            remove_urls: Remove URLs
            remove_emails: Remove email addresses
            remove_extra_whitespace: Normalize whitespace
            lowercase: Convert to lowercase (recommended for Turkish)
            validate_length: Validate text length
        
        Returns:
            Cleaned text ready for embedding
        
        Raises:
            TextTooShortException: If text is too short after cleaning
            TextTooLongException: If text exceeds maximum length
        
        Example:
            >>> processor = TextProcessor()
            >>> text = "<p>İstanbul'da 25 derece sıcaklık var.</p>"
            >>> cleaned = processor.clean_for_embedding(text)
            >>> print(cleaned)
            'istanbul\'da 25 derece sıcaklık var.'
        """
        if not text or not isinstance(text, str):
            raise ValidationException(
                message="Text must be a non-empty string",
                error_code="VAL_004",
            )
        
        # Validate length before processing
        if validate_length and len(text) > MAX_TEXT_LENGTH:
            raise TextTooLongException(len(text), MAX_TEXT_LENGTH)
        
        # Store original for logging
        original_length = len(text)
        
        # Step 1: Decode HTML entities
        text = html.unescape(text)
        
        # Step 2: Remove HTML (scripts, styles, comments, tags)
        if remove_html:
            text = self._remove_html_content(text)
        
        # Step 3: Remove URLs (they don't add semantic value)
        if remove_urls:
            text = self._remove_urls(text)
        
        # Step 4: Remove emails (they don't add semantic value)
        if remove_emails:
            text = self._remove_emails(text)
        
        # Step 5: Normalize unicode (NFC for Turkish)
        text = self._normalize_unicode(text)
        
        # Step 6: Remove only problematic characters
        # PRESERVE: Turkish letters, numbers, basic punctuation
        text = self._remove_problematic_chars(text)
        
        # Step 7: Normalize whitespace
        if remove_extra_whitespace:
            text = self._normalize_whitespace(text)
        
        # Step 8: Turkish-aware lowercase
        if lowercase:
            text = self._turkish_lowercase(text)
        
        # Step 9: Trim
        text = text.strip()
        
        # Validate length after processing
        if validate_length and len(text) < MIN_TEXT_LENGTH:
            raise TextTooShortException(len(text), MIN_TEXT_LENGTH)
        
        # Log cleaning statistics
        cleaned_length = len(text)
        reduction_percent = ((original_length - cleaned_length) / original_length) * 100
        logger.debug(
            f"Text cleaned for embedding: {original_length} → {cleaned_length} chars "
            f"({reduction_percent:.1f}% reduction)"
        )
        
        return text
    
    def prepare_for_similarity_search(self, text: str) -> str:
        """
        Prepare text specifically for similarity search
        
        This is a convenience method that calls clean_for_embedding
        with optimal settings for similarity comparison.
        
        Args:
            text: Input text
        
        Returns:
            Text ready for embedding and similarity search
        """
        return self.clean_for_embedding(
            text,
            remove_html=True,
            remove_urls=True,
            remove_emails=True,
            remove_extra_whitespace=True,
            lowercase=True,
            validate_length=True,
        )
    
    def tokenize(self, text: str, preserve_case: bool = False) -> List[str]:
        """
        Tokenize text into words
        
        Args:
            text: Input text
            preserve_case: Keep original case (default: False)
        
        Returns:
            List of tokens (words)
        
        Example:
            >>> processor = TextProcessor()
            >>> tokens = processor.tokenize("İstanbul'da 25 derece var.")
            >>> print(tokens)
            ['istanbul\'da', '25', 'derece', 'var']
        """
        if not preserve_case:
            text = self._turkish_lowercase(text)
        
        # Simple whitespace tokenization
        tokens = text.split()
        return [token for token in tokens if token]
    
    def remove_stop_words(
        self,
        tokens: List[str],
        custom_stop_words: Optional[Set[str]] = None,
    ) -> List[str]:
        """
        Remove stop words from token list
        
        Args:
            tokens: List of tokens
            custom_stop_words: Additional stop words to remove
        
        Returns:
            Filtered token list
        
        Example:
            >>> processor = TextProcessor()
            >>> tokens = ['bu', 'bir', 'test', '25', 'derece']
            >>> filtered = processor.remove_stop_words(tokens)
            >>> print(filtered)
            ['test', '25', 'derece']  # Numbers preserved!
        """
        stop_words = self.stop_words.copy()
        
        if custom_stop_words:
            stop_words.update(custom_stop_words)
        
        return [token for token in tokens if token.lower() not in stop_words]
    
    def extract_keywords(
        self,
        text: str,
        max_keywords: int = 10,
        min_length: int = 3,
        remove_stop_words: bool = True,
    ) -> List[str]:
        """
        Extract keywords from text
        
        Simple frequency-based keyword extraction.
        
        Args:
            text: Input text
            max_keywords: Maximum number of keywords to return
            min_length: Minimum keyword length
            remove_stop_words: Remove stop words
        
        Returns:
            List of keywords
        
        Example:
            >>> processor = TextProcessor()
            >>> text = "yapay zeka yapay zeka 25 derece 25 derece"
            >>> keywords = processor.extract_keywords(text, max_keywords=3)
            >>> print(keywords)
            ['yapay', 'zeka', '25']  # Numbers can be keywords!
        """
        # Clean text (preserve numbers)
        cleaned = self.clean_for_embedding(text)
        
        # Tokenize
        tokens = self.tokenize(cleaned)
        
        # Remove stop words if requested
        if remove_stop_words:
            tokens = self.remove_stop_words(tokens)
        
        # Filter by length
        tokens = [token for token in tokens if len(token) >= min_length]
        
        # Count frequency
        from collections import Counter
        word_freq = Counter(tokens)
        
        # Get top N keywords
        keywords = [word for word, _ in word_freq.most_common(max_keywords)]
        
        return keywords
    
    # ═══════════════════════════════════════════════════════════
    # EMBEDDING-RELATED METHODS
    # ═══════════════════════════════════════════════════════════
    
    def validate_for_embedding(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if text is suitable for embedding generation
        
        Args:
            text: Text to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        
        Example:
            >>> processor = TextProcessor()
            >>> is_valid, error = processor.validate_for_embedding("Test")
            >>> print(is_valid, error)
            False, "Text too short: 4 chars, minimum 100 required"
        """
        try:
            # Check length
            if len(text) < MIN_TEXT_LENGTH:
                return False, f"Text too short: {len(text)} chars, minimum {MIN_TEXT_LENGTH} required"
            
            if len(text) > MAX_TEXT_LENGTH:
                return False, f"Text too long: {len(text)} chars, maximum {MAX_TEXT_LENGTH} allowed"
            
            # Check if meaningful
            if not self._is_meaningful_text(text):
                return False, "Text does not appear to be meaningful"
            
            # Check if mostly whitespace
            if len(text.strip()) < MIN_TEXT_LENGTH:
                return False, "Text is mostly whitespace"
            
            return True, None
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    # ═══════════════════════════════════════════════════════════
    # PRIVATE HELPER METHODS
    # ═══════════════════════════════════════════════════════════
    
    def _remove_html_content(self, text: str) -> str:
        """Remove all HTML content (scripts, styles, comments, tags)"""
        # Remove scripts
        text = self._script_pattern.sub('', text)
        # Remove styles
        text = self._style_pattern.sub('', text)
        # Remove comments
        text = self._html_comment_pattern.sub('', text)
        # Remove tags
        text = self._html_tag_pattern.sub(' ', text)
        return text
    
    def _remove_urls(self, text: str) -> str:
        """Remove URLs"""
        return self._url_pattern.sub('', text)
    
    def _remove_emails(self, text: str) -> str:
        """Remove email addresses"""
        return self._email_pattern.sub('', text)
    
    def _remove_problematic_chars(self, text: str) -> str:
        """
        Remove only problematic characters
        PRESERVE: Turkish letters (çÇğĞıİöÖşŞüÜ), numbers, basic punctuation
        """
        return self._problematic_chars.sub(' ', text)
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace (spaces, newlines, tabs)"""
        # Replace tabs with spaces
        text = self._multiple_tabs.sub(' ', text)
        # Replace multiple newlines with single newline
        text = self._multiple_newlines.sub('\n', text)
        # Replace multiple spaces with single space
        text = self._multiple_spaces.sub(' ', text)
        # Replace newlines with spaces (for single paragraph processing)
        text = text.replace('\n', ' ')
        return text
    
    def _normalize_unicode(self, text: str) -> str:
        """
        Normalize unicode characters
        
        NFC (Canonical Composition) is recommended for Turkish.
        This ensures consistent representation of characters like ğ, ş, etc.
        """
        return unicodedata.normalize('NFC', text)
    
    def _turkish_lowercase(self, text: str) -> str:
        """
        Turkish-specific lowercase conversion
        
        Critical for Turkish:
        - İ (capital I with dot) → i (lowercase i)
        - I (capital I without dot) → ı (lowercase dotless i)
        
        Standard Python .lower() does NOT handle this correctly!
        """
        # Turkish-specific mappings
        turkish_upper = 'İIÇĞÖŞÜ'
        turkish_lower = 'iıçğöşü'
        
        # Create translation table
        trans_table = str.maketrans(turkish_upper, turkish_lower)
        
        # Apply Turkish mappings first
        text = text.translate(trans_table)
        
        # Then apply standard lowercase for other characters
        text = text.lower()
        
        return text
    
    def _is_meaningful_text(self, text: str, min_words: int = 10) -> bool:
        """
        Check if text appears meaningful
        
        Args:
            text: Text to check
            min_words: Minimum number of words
        
        Returns:
            True if meaningful, False otherwise
        """
        words = text.split()
        
        # Check minimum word count
        if len(words) < min_words:
            return False
        
        # Check average word length (too short or too long = suspicious)
        avg_length = sum(len(word) for word in words) / len(words)
        if avg_length < 2 or avg_length > 20:
            return False
        
        # Check if mostly numbers (probably not an article)
        digit_count = sum(1 for char in text if char.isdigit())
        if digit_count / len(text) > 0.3:  # More than 30% digits
            return False
        
        return True


class TextValidator:
    """
    Text validation utilities
    """
    
    @staticmethod
    def validate_length(
        text: str,
        min_length: int = MIN_TEXT_LENGTH,
        max_length: int = MAX_TEXT_LENGTH,
    ) -> None:
        """
        Validate text length
        
        Args:
            text: Text to validate
            min_length: Minimum allowed length
            max_length: Maximum allowed length
        
        Raises:
            TextTooShortException: If text is too short
            TextTooLongException: If text is too long
        """
        text_length = len(text)
        
        if text_length < min_length:
            raise TextTooShortException(text_length, min_length)
        
        if text_length > max_length:
            raise TextTooLongException(text_length, max_length)
    
    @staticmethod
    def validate_keyword(keyword: str) -> bool:
        """
        Validate keyword format
        
        Args:
            keyword: Keyword to validate
        
        Returns:
            True if valid, False otherwise
        """
        return bool(KEYWORD_PATTERN.match(keyword))
    
    @staticmethod
    def is_turkish_text(text: str) -> bool:
        """
        Check if text appears to be Turkish
        
        Args:
            text: Text to check
        
        Returns:
            True if likely Turkish, False otherwise
        """
        # Count Turkish-specific characters
        turkish_chars = 'çÇğĞıİöÖşŞüÜ'
        turkish_count = sum(1 for char in text if char in turkish_chars)
        
        # If more than 0.5% of characters are Turkish-specific, likely Turkish
        if len(text) > 0:
            ratio = turkish_count / len(text)
            return ratio > 0.005
        
        return False


class TextStatistics:
    """
    Text statistics calculator
    """
    
    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text"""
        return len(text.split())
    
    @staticmethod
    def count_sentences(text: str) -> int:
        """
        Count sentences in text
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s for s in sentences if s.strip()]
        return len(sentences)
    
    @staticmethod
    def count_characters(text: str, include_spaces: bool = True) -> int:
        """Count characters"""
        if include_spaces:
            return len(text)
        else:
            return len(text.replace(' ', ''))
    
    @staticmethod
    def count_numbers(text: str) -> int:
        """Count numerical values in text"""
        numbers = re.findall(r'\d+', text)
        return len(numbers)
    
    @staticmethod
    def count_turkish_chars(text: str) -> int:
        """Count Turkish-specific characters"""
        turkish_chars = 'çÇğĞıİöÖşŞüÜ'
        return sum(1 for char in text if char in turkish_chars)
    
    @staticmethod
    def average_word_length(text: str) -> float:
        """Calculate average word length"""
        words = text.split()
        if not words:
            return 0.0
        return sum(len(word) for word in words) / len(words)
    
    @staticmethod
    def reading_time_minutes(text: str, words_per_minute: int = 200) -> float:
        """
        Estimate reading time in minutes
        
        Args:
            text: Text to analyze
            words_per_minute: Average reading speed (default: 200 wpm)
        
        Returns:
            Estimated reading time in minutes
        """
        word_count = TextStatistics.count_words(text)
        return word_count / words_per_minute
    
    @staticmethod
    def get_statistics(text: str) -> dict:
        """
        Get comprehensive text statistics
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with various statistics
        
        Example:
            >>> stats = TextStatistics.get_statistics("İstanbul'da 25 derece var.")
            >>> print(stats)
            {
                'character_count': 27,
                'word_count': 4,
                'sentence_count': 1,
                'number_count': 1,
                'turkish_char_count': 1,
                'avg_word_length': 5.5,
                'reading_time_minutes': 0.02,
                'is_turkish': True
            }
        """
        return {
            'character_count': TextStatistics.count_characters(text),
            'character_count_no_spaces': TextStatistics.count_characters(text, include_spaces=False),
            'word_count': TextStatistics.count_words(text),
            'sentence_count': TextStatistics.count_sentences(text),
            'number_count': TextStatistics.count_numbers(text),
            'turkish_char_count': TextStatistics.count_turkish_chars(text),
            'avg_word_length': TextStatistics.average_word_length(text),
            'reading_time_minutes': TextStatistics.reading_time_minutes(text),
            'is_turkish': TextValidator.is_turkish_text(text),
        }


# ═══════════════════════════════════════════════════════════
# HELPER FUNCTIONS (Functional API)
# ═══════════════════════════════════════════════════════════

def clean_for_embedding(text: str) -> str:
    """
    Convenience function for cleaning text for embedding
    
    Args:
        text: Text to clean
    
    Returns:
        Cleaned text ready for embedding generation
    
    Example:
        >>> cleaned = clean_for_embedding("<p>İstanbul'da 25 derece.</p>")
        >>> print(cleaned)
        'istanbul\'da 25 derece.'
    """
    processor = TextProcessor()
    return processor.clean_for_embedding(text)


def prepare_for_similarity_search(text: str) -> str:
    """
    Convenience function for preparing text for similarity search
    
    Args:
        text: Text to prepare
    
    Returns:
        Text ready for similarity search
    """
    processor = TextProcessor()
    return processor.prepare_for_similarity_search(text)


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Convenience function for keyword extraction
    
    Args:
        text: Text to extract keywords from
        max_keywords: Maximum number of keywords
    
    Returns:
        List of keywords
    """
    processor = TextProcessor()
    return processor.extract_keywords(text, max_keywords=max_keywords)


def get_text_stats(text: str) -> dict:
    """
    Convenience function for text statistics
    
    Args:
        text: Text to analyze
    
    Returns:
        Dictionary with statistics
    """
    return TextStatistics.get_statistics(text)


# ═══════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Example 1: Cleaning for embedding (MAIN USE CASE)
    print("=== Example 1: Clean for Embedding ===")
    processor = TextProcessor()
    
    raw_text = """
    <p>İstanbul'da hava sıcaklığı 25 derece olarak ölçüldü.</p>
    <a href="http://example.com">Detaylar</a>
    Email: haber@example.com
    """
    
    cleaned = processor.clean_for_embedding(raw_text)
    print(f"Original: {raw_text}")
    print(f"Cleaned: {cleaned}")
    print(f"Notice: Turkish chars (İ→i) preserved, number (25) preserved!")
    print()
    
    # Example 2: Turkish lowercase test
    print("=== Example 2: Turkish Lowercase ===")
    test_cases = [
        "İSTANBUL",  # İ → i (not I → i)
        "IĞDIR",     # I → ı (not I → i)
        "ÇAĞRI",     # Ç → ç, Ğ → ğ
    ]
    
    for test in test_cases:
        lowered = processor._turkish_lowercase(test)
        print(f"{test} → {lowered}")
    print()
    
    # Example 3: Numbers preserved
    print("=== Example 3: Numbers Preserved ===")
    news_text = "2024 yılında 15 milyon kişi İstanbul'u ziyaret etti."
    cleaned = processor.clean_for_embedding(news_text)
    print(f"Original: {news_text}")
    print(f"Cleaned: {cleaned}")
    print(f"Numbers preserved: {'2024' in cleaned and '15' in cleaned}")
    print()
    
    # Example 4: Statistics with Turkish detection
    print("=== Example 4: Text Statistics ===")
    article = "İstanbul'da 25 derece sıcaklık var. Güneşli hava bekleniyor."
    stats = TextStatistics.get_statistics(article)
    print(f"Text: {article}")
    print(f"Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()
    
    # Example 5: Validation
    print("=== Example 5: Validation ===")
    is_valid, error = processor.validate_for_embedding(article)
    print(f"Is valid for embedding: {is_valid}")
    if error:
        print(f"Error: {error}")
    """
    Text processing and cleaning for NLP pipeline
    
    Handles Turkish text preprocessing including:
    - HTML tag removal
    - Special character cleaning
    - Whitespace normalization
    - Stop word removal
    - Unicode normalization
    """
    
    def __init__(self, language: str = "tr"):
        """
        Initialize text processor
        
        Args:
            language: Language code (default: 'tr' for Turkish)
        """
        self.language = language
        self.stop_words = TURKISH_STOP_WORDS
        
        # Compile regex patterns for performance
        self._html_tag_pattern = re.compile(r'<[^>]+>')
        self._url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        self._email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
        self._multiple_spaces = re.compile(r'\s+')
        self._multiple_newlines = re.compile(r'\n+')
        self._special_chars = re.compile(r'[^\w\s\.,!?;:\-çÇğĞıİöÖşŞüÜ]')
        self._digit_pattern = re.compile(r'\d+')
        
        logger.info(f"TextProcessor initialized for language: {language}")
    
    def clean(
        self,
        text: str,
        *,
        remove_html: bool = True,
        remove_urls: bool = True,
        remove_emails: bool = True,
        remove_special_chars: bool = True,
        remove_digits: bool = False,
        remove_extra_whitespace: bool = True,
        lowercase: bool = True,
        validate_length: bool = True,
    ) -> str:
        """
        Main cleaning pipeline
        
        Args:
            text: Input text to clean
            remove_html: Remove HTML tags
            remove_urls: Remove URLs
            remove_emails: Remove email addresses
            remove_special_chars: Remove special characters
            remove_digits: Remove all digits
            remove_extra_whitespace: Normalize whitespace
            lowercase: Convert to lowercase
            validate_length: Validate text length
        
        Returns:
            Cleaned text
        
        Raises:
            TextTooShortException: If text is too short after cleaning
            TextTooLongException: If text exceeds maximum length
        
        Example:
            >>> processor = TextProcessor()
            >>> text = "<p>Bu bir <b>test</b> metnidir.</p>"
            >>> cleaned = processor.clean(text)
            >>> print(cleaned)
            'bu bir test metnidir.'
        """
        if not text or not isinstance(text, str):
            raise ValidationException(
                message="Text must be a non-empty string",
                error_code="VAL_004",
            )
        
        # Validate length before processing
        if validate_length and len(text) > MAX_TEXT_LENGTH:
            raise TextTooLongException(len(text), MAX_TEXT_LENGTH)
        
        # Store original length for logging
        original_length = len(text)
        
        # Step 1: Decode HTML entities
        text = html.unescape(text)
        
        # Step 2: Remove HTML tags
        if remove_html:
            text = self._remove_html_tags(text)
        
        # Step 3: Remove URLs
        if remove_urls:
            text = self._remove_urls(text)
        
        # Step 4: Remove emails
        if remove_emails:
            text = self._remove_emails(text)
        
        # Step 5: Normalize unicode characters
        text = self._normalize_unicode(text)
        
        # Step 6: Remove digits (optional)
        if remove_digits:
            text = self._remove_digits(text)
        
        # Step 7: Remove special characters
        if remove_special_chars:
            text = self._remove_special_chars(text)
        
        # Step 8: Normalize whitespace
        if remove_extra_whitespace:
            text = self._normalize_whitespace(text)
        
        # Step 9: Convert to lowercase
        if lowercase:
            text = text.lower()
        
        # Step 10: Trim
        text = text.strip()
        
        # Validate length after processing
        if validate_length and len(text) < MIN_TEXT_LENGTH:
            raise TextTooShortException(len(text), MIN_TEXT_LENGTH)
        
        # Log cleaning statistics
        cleaned_length = len(text)
        reduction_percent = ((original_length - cleaned_length) / original_length) * 100
        logger.debug(
            f"Text cleaned: {original_length} → {cleaned_length} chars "
            f"({reduction_percent:.1f}% reduction)"
        )
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words
        
        Args:
            text: Input text
        
        Returns:
            List of tokens (words)
        
        Example:
            >>> processor = TextProcessor()
            >>> tokens = processor.tokenize("Bu bir test metnidir.")
            >>> print(tokens)
            ['Bu', 'bir', 'test', 'metnidir']
        """
        # Simple whitespace tokenization
        # For more advanced tokenization, use spaCy
        tokens = text.split()
        return [token for token in tokens if token]
    
    def remove_stop_words(
        self,
        tokens: List[str],
        custom_stop_words: Optional[Set[str]] = None,
    ) -> List[str]:
        """
        Remove stop words from token list
        
        Args:
            tokens: List of tokens
            custom_stop_words: Additional stop words to remove
        
        Returns:
            Filtered token list
        
        Example:
            >>> processor = TextProcessor()
            >>> tokens = ['bu', 'bir', 'test', 'metnidir']
            >>> filtered = processor.remove_stop_words(tokens)
            >>> print(filtered)
            ['test', 'metnidir']
        """
        stop_words = self.stop_words.copy()
        
        if custom_stop_words:
            stop_words.update(custom_stop_words)
        
        return [token for token in tokens if token.lower() not in stop_words]
    
    def extract_keywords(
        self,
        text: str,
        max_keywords: int = 10,
        min_length: int = 3,
        remove_stop_words: bool = True,
    ) -> List[str]:
        """
        Extract keywords from text
        
        Simple frequency-based keyword extraction.
        For better results, use TF-IDF or RAKE algorithm.
        
        Args:
            text: Input text
            max_keywords: Maximum number of keywords to return
            min_length: Minimum keyword length
            remove_stop_words: Remove stop words
        
        Returns:
            List of keywords
        
        Example:
            >>> processor = TextProcessor()
            >>> text = "yapay zeka teknolojisi gelişiyor. yapay zeka..."
            >>> keywords = processor.extract_keywords(text, max_keywords=3)
            >>> print(keywords)
            ['yapay', 'zeka', 'teknolojisi']
        """
        # Clean text
        cleaned = self.clean(text, remove_digits=True, lowercase=True)
        
        # Tokenize
        tokens = self.tokenize(cleaned)
        
        # Remove stop words if requested
        if remove_stop_words:
            tokens = self.remove_stop_words(tokens)
        
        # Filter by length
        tokens = [token for token in tokens if len(token) >= min_length]
        
        # Count frequency
        from collections import Counter
        word_freq = Counter(tokens)
        
        # Get top N keywords
        keywords = [word for word, _ in word_freq.most_common(max_keywords)]
        
        return keywords
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text for embedding/similarity comparison
        
        This is the standard preprocessing for NLP models.
        
        Args:
            text: Input text
        
        Returns:
            Normalized text
        
        Example:
            >>> processor = TextProcessor()
            >>> text = "<p>BU BİR TEST METNİDİR!!!</p>"
            >>> normalized = processor.normalize_text(text)
            >>> print(normalized)
            'bu bir test metnidir'
        """
        return self.clean(
            text,
            remove_html=True,
            remove_urls=True,
            remove_emails=True,
            remove_special_chars=True,
            remove_digits=False,
            remove_extra_whitespace=True,
            lowercase=True,
            validate_length=True,
        )
    
    # ═══════════════════════════════════════════════════════════
    # PRIVATE HELPER METHODS
    # ═══════════════════════════════════════════════════════════
    
    def _remove_html_tags(self, text: str) -> str:
        """Remove HTML tags"""
        return self._html_tag_pattern.sub('', text)
    
    def _remove_urls(self, text: str) -> str:
        """Remove URLs"""
        return self._url_pattern.sub('', text)
    
    def _remove_emails(self, text: str) -> str:
        """Remove email addresses"""
        return self._email_pattern.sub('', text)
    
    def _remove_special_chars(self, text: str) -> str:
        """
        Remove special characters but keep Turkish characters
        and basic punctuation
        """
        return self._special_chars.sub(' ', text)
    
    def _remove_digits(self, text: str) -> str:
        """Remove all digits"""
        return self._digit_pattern.sub('', text)
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace (spaces, newlines, tabs)"""
        # Replace multiple newlines with single newline
        text = self._multiple_newlines.sub('\n', text)
        # Replace multiple spaces with single space
        text = self._multiple_spaces.sub(' ', text)
        return text
    
    def _normalize_unicode(self, text: str) -> str:
        """
        Normalize unicode characters
        
        NFC (Canonical Decomposition, followed by Canonical Composition)
        is the recommended normalization form for Turkish text.
        """
        return unicodedata.normalize('NFC', text)
    
    def _turkish_lowercase(self, text: str) -> str:
        """
        Turkish-specific lowercase conversion
        
        Handles Turkish special case: İ → i, I → ı
        """
        # Turkish lowercase mapping
        turkish_map = str.maketrans('İIÇĞÖŞÜ', 'iıçğöşü')
        return text.translate(turkish_map).lower()


class TextValidator:
    """
    Text validation utilities
    """
    
    @staticmethod
    def validate_length(
        text: str,
        min_length: int = MIN_TEXT_LENGTH,
        max_length: int = MAX_TEXT_LENGTH,
    ) -> None:
        """
        Validate text length
        
        Args:
            text: Text to validate
            min_length: Minimum allowed length
            max_length: Maximum allowed length
        
        Raises:
            TextTooShortException: If text is too short
            TextTooLongException: If text is too long
        """
        text_length = len(text)
        
        if text_length < min_length:
            raise TextTooShortException(text_length, min_length)
        
        if text_length > max_length:
            raise TextTooLongException(text_length, max_length)
    
    @staticmethod
    def validate_keyword(keyword: str) -> bool:
        """
        Validate keyword format
        
        Args:
            keyword: Keyword to validate
        
        Returns:
            True if valid, False otherwise
        """
        return bool(KEYWORD_PATTERN.match(keyword))
    
    @staticmethod
    def is_meaningful_text(text: str, min_words: int = 10) -> bool:
        """
        Check if text is meaningful (not just gibberish)
        
        Args:
            text: Text to check
            min_words: Minimum number of words
        
        Returns:
            True if meaningful, False otherwise
        """
        words = text.split()
        
        # Check minimum word count
        if len(words) < min_words:
            return False
        
        # Check average word length (gibberish usually has weird lengths)
        avg_length = sum(len(word) for word in words) / len(words)
        if avg_length < 2 or avg_length > 15:
            return False
        
        return True


class TextStatistics:
    """
    Text statistics calculator
    """
    
    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text"""
        return len(text.split())
    
    @staticmethod
    def count_sentences(text: str) -> int:
        """
        Count sentences in text
        
        Simple sentence counter based on punctuation.
        """
        # Split by sentence-ending punctuation
        sentences = re.split(r'[.!?]+', text)
        # Filter empty strings
        sentences = [s for s in sentences if s.strip()]
        return len(sentences)
    
    @staticmethod
    def count_characters(text: str, include_spaces: bool = True) -> int:
        """Count characters"""
        if include_spaces:
            return len(text)
        else:
            return len(text.replace(' ', ''))
    
    @staticmethod
    def average_word_length(text: str) -> float:
        """Calculate average word length"""
        words = text.split()
        if not words:
            return 0.0
        return sum(len(word) for word in words) / len(words)
    
    @staticmethod
    def reading_time_minutes(text: str, words_per_minute: int = 200) -> float:
        """
        Estimate reading time in minutes
        
        Args:
            text: Text to analyze
            words_per_minute: Average reading speed (default: 200 wpm)
        
        Returns:
            Estimated reading time in minutes
        """
        word_count = TextStatistics.count_words(text)
        return word_count / words_per_minute
    
    @staticmethod
    def get_statistics(text: str) -> dict:
        """
        Get comprehensive text statistics
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with various statistics
        
        Example:
            >>> stats = TextStatistics.get_statistics("Bu bir test metnidir.")
            >>> print(stats)
            {
                'character_count': 22,
                'word_count': 4,
                'sentence_count': 1,
                'avg_word_length': 4.5,
                'reading_time_minutes': 0.02
            }
        """
        return {
            'character_count': TextStatistics.count_characters(text),
            'character_count_no_spaces': TextStatistics.count_characters(text, include_spaces=False),
            'word_count': TextStatistics.count_words(text),
            'sentence_count': TextStatistics.count_sentences(text),
            'avg_word_length': TextStatistics.average_word_length(text),
            'reading_time_minutes': TextStatistics.reading_time_minutes(text),
        }


# ═══════════════════════════════════════════════════════════
# HELPER FUNCTIONS (Functional API)
# ═══════════════════════════════════════════════════════════

def clean_text(text: str, **kwargs) -> str:
    """
    Convenience function for text cleaning
    
    Args:
        text: Text to clean
        **kwargs: Keyword arguments passed to TextProcessor.clean()
    
    Returns:
        Cleaned text
    
    Example:
        >>> cleaned = clean_text("<p>Test</p>", remove_html=True)
        >>> print(cleaned)
        'test'
    """
    processor = TextProcessor()
    return processor.clean(text, **kwargs)


def normalize_text(text: str) -> str:
    """
    Convenience function for text normalization
    
    Args:
        text: Text to normalize
    
    Returns:
        Normalized text
    """
    processor = TextProcessor()
    return processor.normalize_text(text)


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Convenience function for keyword extraction
    
    Args:
        text: Text to extract keywords from
        max_keywords: Maximum number of keywords
    
    Returns:
        List of keywords
    """
    processor = TextProcessor()
    return processor.extract_keywords(text, max_keywords=max_keywords)


def get_text_stats(text: str) -> dict:
    """
    Convenience function for text statistics
    
    Args:
        text: Text to analyze
    
    Returns:
        Dictionary with statistics
    """
    return TextStatistics.get_statistics(text)


# ═══════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Example 1: Basic cleaning
    print("=== Example 1: Basic Cleaning ===")
    processor = TextProcessor()
    
    raw_text = """
    <p>Bu bir <b>test</b> metnidir!!!</p>
    <a href="http://example.com">Link</a>
    Email: test@example.com
    """
    
    cleaned = processor.clean(raw_text)
    print(f"Original: {raw_text}")
    print(f"Cleaned: {cleaned}")
    print()
    
    # Example 2: Keyword extraction
    print("=== Example 2: Keyword Extraction ===")
    article_text = """
    Yapay zeka teknolojisi hızla gelişiyor. Yapay zeka, 
    makine öğrenmesi ve derin öğrenme gibi teknolojiler 
    sayesinde birçok alanda kullanılmaktadır. Yapay zeka 
    uygulamaları gün geçtikçe yaygınlaşıyor.
    """
    
    keywords = processor.extract_keywords(article_text, max_keywords=5)
    print(f"Text: {article_text[:100]}...")
    print(f"Keywords: {keywords}")
    print()
    
    # Example 3: Text statistics
    print("=== Example 3: Text Statistics ===")
    stats = TextStatistics.get_statistics(article_text)
    print(f"Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()
    
    # Example 4: Validation
    print("=== Example 4: Validation ===")
    short_text = "Test"
    try:
        TextValidator.validate_length(short_text)
    except TextTooShortException as e:
        print(f"Validation failed: {e.message}")
        print(f"Error code: {e.error_code}")
        print(f"Details: {e.details}")
    print()
    
    # Example 5: Stop word removal
    print("=== Example 5: Stop Word Removal ===")
    tokens = ["bu", "bir", "test", "metnidir", "ve", "çok", "güzel"]
    filtered = processor.remove_stop_words(tokens)
    print(f"Original tokens: {tokens}")
    print(f"After stop word removal: {filtered}")