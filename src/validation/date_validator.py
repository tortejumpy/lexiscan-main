"""
Date Validation and Standardization
"""

import logging
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)


class DateValidator:
    """
    Validate and standardize date entities
    """
    
    def __init__(self):
        """Initialize date validator"""
        self.date_formats = [
            "%B %d, %Y",      # January 1, 2024
            "%m/%d/%Y",       # 01/01/2024
            "%Y-%m-%d",       # 2024-01-01
            "%d %B %Y",       # 1 January 2024
            "%b %d, %Y",      # Jan 1, 2024
            "%d-%m-%Y",       # 01-01-2024
        ]
        
        logger.info("DateValidator initialized")
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string to datetime object
        
        Args:
            date_str: Date string
            
        Returns:
            Datetime object or None
        """
        try:
            # Try dateutil parser (flexible)
            return date_parser.parse(date_str, fuzzy=True)
        except:
            # Try manual formats
            for fmt in self.date_formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except:
                    continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def standardize_date(self, date_str: str, format: str = "iso") -> Optional[str]:
        """
        Standardize date to ISO 8601 or custom format
        
        Args:
            date_str: Date string
            format: Output format ('iso' or strftime format)
            
        Returns:
            Standardized date string or None
        """
        dt = self.parse_date(date_str)
        
        if dt is None:
            return None
        
        if format == "iso":
            return dt.strftime("%Y-%m-%d")
        else:
            try:
                return dt.strftime(format)
            except:
                return dt.strftime("%Y-%m-%d")
    
    def validate_date_consistency(
        self,
        effective_date: Optional[str],
        termination_date: Optional[str],
        expiration_date: Optional[str]
    ) -> Dict[str, bool]:
        """
        Validate date consistency rules
        
        Args:
            effective_date: Effective date string
            termination_date: Termination date string
            expiration_date: Expiration date string
            
        Returns:
            Dictionary with validation results
        """
        results = {
            'valid': True,
            'errors': []
        }
        
        # Parse dates
        eff_dt = self.parse_date(effective_date) if effective_date else None
        term_dt = self.parse_date(termination_date) if termination_date else None
        exp_dt = self.parse_date(expiration_date) if expiration_date else None
        
        # Rule 1: Termination date must be after effective date
        if eff_dt and term_dt:
            if term_dt <= eff_dt:
                results['valid'] = False
                results['errors'].append(
                    f"Termination date ({termination_date}) must be after "
                    f"effective date ({effective_date})"
                )
        
        # Rule 2: Expiration date must be after effective date
        if eff_dt and exp_dt:
            if exp_dt <= eff_dt:
                results['valid'] = False
                results['errors'].append(
                    f"Expiration date ({expiration_date}) must be after "
                    f"effective date ({effective_date})"
                )
        
        # Rule 3: Dates should be reasonable (not too far in past/future)
        current_year = datetime.now().year
        
        for date_name, dt in [('effective', eff_dt), ('termination', term_dt), ('expiration', exp_dt)]:
            if dt:
                if dt.year < 1900 or dt.year > current_year + 100:
                    results['valid'] = False
                    results['errors'].append(
                        f"{date_name.capitalize()} date year ({dt.year}) is unreasonable"
                    )
        
        return results
    
    def extract_date_entities(self, entities: List[Dict]) -> Dict[str, Optional[str]]:
        """
        Extract and categorize date entities
        
        Args:
            entities: List of entity dictionaries
            
        Returns:
            Dictionary with categorized dates
        """
        dates = {
            'effective_date': None,
            'termination_date': None,
            'expiration_date': None,
            'agreement_date': None,
            'other_dates': []
        }
        
        for entity in entities:
            if entity['label'] == 'DATE':
                text = entity['text'].lower()
                
                # Categorize based on context
                if 'effective' in text or entity.get('context', '').lower().find('effective') != -1:
                    dates['effective_date'] = entity['text']
                elif 'termination' in text or 'terminat' in entity.get('context', '').lower():
                    dates['termination_date'] = entity['text']
                elif 'expiration' in text or 'expir' in entity.get('context', '').lower():
                    dates['expiration_date'] = entity['text']
                elif 'agreement' in text or 'dated' in entity.get('context', '').lower():
                    dates['agreement_date'] = entity['text']
                else:
                    dates['other_dates'].append(entity['text'])
        
        return dates
