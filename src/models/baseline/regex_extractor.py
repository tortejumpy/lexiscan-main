"""
Regex-based Entity Extractor for Legal Contracts
Baseline approach using pattern matching
"""

import re
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ExtractedEntity:
    """Container for extracted entity"""
    text: str
    label: str
    start: int
    end: int
    confidence: float = 1.0


class RegexExtractor:
    """
    Rule-based entity extraction using regex patterns
    """
    
    def __init__(self):
        """Initialize regex patterns for different entity types"""
        
        # Date patterns
        self.date_patterns = [
            # January 1, 2024
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            # 01/01/2024, 1-1-2024
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            # 2024-01-01
            r'\b\d{4}-\d{2}-\d{2}\b',
            # 1st January 2024
            r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
        ]
        
        # Amount patterns
        self.amount_patterns = [
            # $500,000 or $500,000.00
            r'\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b',
            # USD 500,000
            r'\b(?:USD|EUR|GBP)\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b',
            # 500,000 dollars
            r'\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s+(?:dollars|USD|euros|pounds)\b',
        ]
        
        # Jurisdiction patterns
        self.jurisdiction_patterns = [
            # State of California
            r'\bState\s+of\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b',
            # California, New York
            r'\b(?:Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New\s+Hampshire|New\s+Jersey|New\s+Mexico|New\s+York|North\s+Carolina|North\s+Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode\s+Island|South\s+Carolina|South\s+Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West\s+Virginia|Wisconsin|Wyoming)\b',
            # United Kingdom, Canada, etc.
            r'\b(?:United\s+Kingdom|Canada|Australia|Germany|France|Japan|China)\b',
        ]
        
        # Party patterns (company names)
        self.party_patterns = [
            # Inc., Corp., LLC, Ltd.
            r'\b[A-Z][A-Za-z\s&]+(?:Inc\.|Corp\.|LLC|Ltd\.|L\.P\.|LLP)\b',
            # All caps company names
            r'\b[A-Z]{2,}(?:\s+[A-Z]{2,})*\b',
        ]
        
        # Term patterns
        self.term_patterns = [
            # 3 years, three years
            r'\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+(?:year|month|day)s?\b',
            # successive 1 year
            r'\bsuccessive\s+\d+\s+(?:year|month)s?\b',
        ]
        
        logger.info("RegexExtractor initialized with pattern matching rules")
    
    def extract_dates(self, text: str) -> List[ExtractedEntity]:
        """Extract date entities"""
        entities = []
        
        for pattern in self.date_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(ExtractedEntity(
                    text=match.group(),
                    label='DATE',
                    start=match.start(),
                    end=match.end(),
                    confidence=0.9
                ))
        
        return entities
    
    def extract_amounts(self, text: str) -> List[ExtractedEntity]:
        """Extract monetary amount entities"""
        entities = []
        
        for pattern in self.amount_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(ExtractedEntity(
                    text=match.group(),
                    label='AMOUNT',
                    start=match.start(),
                    end=match.end(),
                    confidence=0.85
                ))
        
        return entities
    
    def extract_jurisdictions(self, text: str) -> List[ExtractedEntity]:
        """Extract jurisdiction entities"""
        entities = []
        
        for pattern in self.jurisdiction_patterns:
            for match in re.finditer(pattern, text):
                entities.append(ExtractedEntity(
                    text=match.group(),
                    label='JURISDICTION',
                    start=match.start(),
                    end=match.end(),
                    confidence=0.8
                ))
        
        return entities
    
    def extract_parties(self, text: str) -> List[ExtractedEntity]:
        """Extract party (company) entities"""
        entities = []
        
        for pattern in self.party_patterns:
            for match in re.finditer(pattern, text):
                # Filter out common false positives
                party_text = match.group()
                if len(party_text) > 3 and not self._is_false_positive_party(party_text):
                    entities.append(ExtractedEntity(
                        text=party_text,
                        label='PARTY',
                        start=match.start(),
                        end=match.end(),
                        confidence=0.7
                    ))
        
        return entities
    
    def extract_terms(self, text: str) -> List[ExtractedEntity]:
        """Extract contract term entities"""
        entities = []
        
        for pattern in self.term_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(ExtractedEntity(
                    text=match.group(),
                    label='TERM',
                    start=match.start(),
                    end=match.end(),
                    confidence=0.75
                ))
        
        return entities
    
    def _is_false_positive_party(self, text: str) -> bool:
        """Filter out common false positives for party names"""
        false_positives = [
            'THE', 'AND', 'FOR', 'WITH', 'THIS', 'THAT',
            'AGREEMENT', 'CONTRACT', 'SECTION', 'ARTICLE'
        ]
        return text.upper() in false_positives
    
    def extract_all(self, text: str) -> List[ExtractedEntity]:
        """
        Extract all entity types from text
        
        Args:
            text: Input text
            
        Returns:
            List of extracted entities
        """
        all_entities = []
        
        # Extract each entity type
        all_entities.extend(self.extract_dates(text))
        all_entities.extend(self.extract_amounts(text))
        all_entities.extend(self.extract_jurisdictions(text))
        all_entities.extend(self.extract_parties(text))
        all_entities.extend(self.extract_terms(text))
        
        # Remove duplicates and overlaps
        all_entities = self._remove_overlaps(all_entities)
        
        # Sort by position
        all_entities.sort(key=lambda e: e.start)
        
        logger.info(f"Extracted {len(all_entities)} entities using regex patterns")
        
        return all_entities
    
    def _remove_overlaps(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """Remove overlapping entities, keeping higher confidence ones"""
        if not entities:
            return []
        
        # Sort by start position, then by confidence
        sorted_entities = sorted(entities, key=lambda e: (e.start, -e.confidence))
        
        filtered = []
        last_end = -1
        
        for entity in sorted_entities:
            if entity.start >= last_end:
                filtered.append(entity)
                last_end = entity.end
        
        return filtered
    
    def get_entity_summary(self, entities: List[ExtractedEntity]) -> Dict[str, int]:
        """
        Get summary statistics of extracted entities
        
        Args:
            entities: List of entities
            
        Returns:
            Dictionary with entity counts by type
        """
        summary = {}
        
        for entity in entities:
            summary[entity.label] = summary.get(entity.label, 0) + 1
        
        return summary
