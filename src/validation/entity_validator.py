"""
Entity Validation and Consistency Checking
"""

import logging
import re
from typing import List, Dict, Optional, Set

logger = logging.getLogger(__name__)


class EntityValidator:
    """
    Validate extracted entities for consistency and correctness
    """
    
    def __init__(self):
        """Initialize entity validator"""
        logger.info("EntityValidator initialized")
    
    def validate_party_names(self, entities: List[Dict]) -> Dict[str, bool]:
        """
        Validate party name entities
        
        Args:
            entities: List of entity dictionaries
            
        Returns:
            Validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        party_entities = [e for e in entities if e['label'] == 'PARTY']
        
        if not party_entities:
            results['warnings'].append("No party entities found")
            return results
        
        # Check for duplicate parties
        party_texts = [e['text'] for e in party_entities]
        unique_parties = set(party_texts)
        
        if len(unique_parties) < 2:
            results['warnings'].append(
                "Expected at least 2 unique parties in contract"
            )
        
        # Check for very short party names (likely errors)
        for party in party_entities:
            if len(party['text']) < 3:
                results['valid'] = False
                results['errors'].append(
                    f"Party name too short: '{party['text']}'"
                )
        
        return results
    
    def validate_amounts(self, entities: List[Dict]) -> Dict[str, bool]:
        """
        Validate monetary amount entities
        
        Args:
            entities: List of entity dictionaries
            
        Returns:
            Validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        amount_entities = [e for e in entities if e['label'] == 'AMOUNT']
        
        for amount in amount_entities:
            text = amount['text']
            
            # Extract numeric value
            numeric_match = re.search(r'[\d,]+(?:\.\d{2})?', text)
            
            if not numeric_match:
                results['valid'] = False
                results['errors'].append(
                    f"Could not extract numeric value from amount: '{text}'"
                )
                continue
            
            # Check for reasonable range
            try:
                value_str = numeric_match.group().replace(',', '')
                value = float(value_str)
                
                if value < 0:
                    results['valid'] = False
                    results['errors'].append(
                        f"Negative amount found: '{text}'"
                    )
                elif value > 1e12:  # 1 trillion
                    results['warnings'].append(
                        f"Unusually large amount: '{text}'"
                    )
            except:
                results['errors'].append(
                    f"Could not parse amount value: '{text}'"
                )
        
        return results
    
    def validate_jurisdictions(self, entities: List[Dict]) -> Dict[str, bool]:
        """
        Validate jurisdiction entities
        
        Args:
            entities: List of entity dictionaries
            
        Returns:
            Validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        jurisdiction_entities = [e for e in entities if e['label'] == 'JURISDICTION']
        
        if not jurisdiction_entities:
            results['warnings'].append("No jurisdiction found")
        elif len(jurisdiction_entities) > 3:
            results['warnings'].append(
                f"Multiple jurisdictions found ({len(jurisdiction_entities)})"
            )
        
        return results
    
    def check_entity_overlaps(self, entities: List[Dict]) -> Dict[str, bool]:
        """
        Check for overlapping entities
        
        Args:
            entities: List of entity dictionaries
            
        Returns:
            Validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'overlaps': []
        }
        
        # Sort by start position
        sorted_entities = sorted(entities, key=lambda e: e['start'])
        
        for i in range(len(sorted_entities) - 1):
            current = sorted_entities[i]
            next_entity = sorted_entities[i + 1]
            
            # Check for overlap
            if current['end'] > next_entity['start']:
                overlap_info = {
                    'entity1': current,
                    'entity2': next_entity
                }
                results['overlaps'].append(overlap_info)
                results['errors'].append(
                    f"Overlapping entities: [{current['label']}] '{current['text']}' "
                    f"and [{next_entity['label']}] '{next_entity['text']}'"
                )
                results['valid'] = False
        
        return results
    
    def validate_all(self, entities: List[Dict]) -> Dict[str, any]:
        """
        Run all validation checks
        
        Args:
            entities: List of entity dictionaries
            
        Returns:
            Combined validation results
        """
        results = {
            'overall_valid': True,
            'party_validation': self.validate_party_names(entities),
            'amount_validation': self.validate_amounts(entities),
            'jurisdiction_validation': self.validate_jurisdictions(entities),
            'overlap_check': self.check_entity_overlaps(entities),
            'total_errors': 0,
            'total_warnings': 0
        }
        
        # Aggregate errors and warnings
        for key, validation in results.items():
            if isinstance(validation, dict):
                if not validation.get('valid', True):
                    results['overall_valid'] = False
                
                results['total_errors'] += len(validation.get('errors', []))
                results['total_warnings'] += len(validation.get('warnings', []))
        
        logger.info(f"Validation completed: {results['total_errors']} errors, "
                   f"{results['total_warnings']} warnings")
        
        return results
