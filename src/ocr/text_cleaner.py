"""
Text cleaning and normalization utilities
"""

import re
import logging
from typing import List, Dict
import unicodedata

logger = logging.getLogger(__name__)


class TextCleaner:
    """
    Clean and normalize OCR-extracted text
    """
    
    def __init__(self):
        """Initialize text cleaner"""
        self.whitespace_pattern = re.compile(r'\s+')
        self.special_chars_pattern = re.compile(r'[^\w\s\.,;:!?\-\$\(\)\"\'\/]')
        
    def remove_extra_whitespace(self, text: str) -> str:
        """
        Remove extra whitespace and normalize spacing
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        # Replace multiple spaces with single space
        text = self.whitespace_pattern.sub(' ', text)
        
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        
        # Remove empty lines
        lines = [line for line in lines if line]
        
        return '\n'.join(lines)
    
    def fix_common_ocr_errors(self, text: str) -> str:
        """
        Fix common OCR recognition errors
        
        Args:
            text: Input text
            
        Returns:
            Corrected text
        """
        # Common OCR substitutions
        corrections = {
            r'\b0\b': 'O',  # Zero to letter O
            r'\bl\b': 'I',  # lowercase L to uppercase I in certain contexts
            r'rn': 'm',     # rn often misread as m
            r'\|': 'I',     # Pipe to I
            r'~': '-',      # Tilde to dash
        }
        
        for pattern, replacement in corrections.items():
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def normalize_unicode(self, text: str) -> str:
        """
        Normalize Unicode characters
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
        # Normalize to NFKD form and encode to ASCII
        text = unicodedata.normalize('NFKD', text)
        text = text.encode('ascii', 'ignore').decode('ascii')
        
        return text
    
    def remove_page_numbers(self, text: str) -> str:
        """
        Remove page numbers and headers/footers
        
        Args:
            text: Input text
            
        Returns:
            Text without page numbers
        """
        # Remove standalone numbers at start/end of lines
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Remove "Page X of Y" patterns
        text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', text, flags=re.IGNORECASE)
        
        return text
    
    def clean_text(
        self,
        text: str,
        remove_whitespace: bool = True,
        fix_ocr_errors: bool = True,
        normalize: bool = True,
        remove_pages: bool = True
    ) -> str:
        """
        Apply all cleaning operations
        
        Args:
            text: Input text
            remove_whitespace: Remove extra whitespace
            fix_ocr_errors: Fix common OCR errors
            normalize: Normalize Unicode
            remove_pages: Remove page numbers
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Apply cleaning operations
        if normalize:
            text = self.normalize_unicode(text)
        
        if fix_ocr_errors:
            text = self.fix_common_ocr_errors(text)
        
        if remove_pages:
            text = self.remove_page_numbers(text)
        
        if remove_whitespace:
            text = self.remove_extra_whitespace(text)
        
        logger.debug(f"Cleaned text: {len(text)} characters")
        
        return text
    
    def extract_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def get_text_statistics(self, text: str) -> Dict[str, int]:
        """
        Calculate text statistics
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with statistics
        """
        words = text.split()
        sentences = self.extract_sentences(text)
        
        stats = {
            'total_characters': len(text),
            'total_words': len(words),
            'total_sentences': len(sentences),
            'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0,
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0
        }
        
        return stats
