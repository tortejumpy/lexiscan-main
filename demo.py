"""
Demo script for LexiScan Auto NER system
Demonstrates baseline NER model (no heavy dependencies required)
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import only baseline model - works without Spacy/PyTorch
from src.models.baseline import BaselineNERModel
from src.utils.helpers import setup_logging

# Setup logging
setup_logging(log_file='logs/demo.log', log_level='INFO')
logger = logging.getLogger(__name__)


def demo_baseline_ner():
    """Demonstrate baseline NER model"""
    
    print("="*70)
    print("LexiScan Auto - Intelligent Legal Document Parser")
    print("="*70)
    print()
    
    # Initialize model
    logger.info("Initializing Baseline NER Model...")
    model = BaselineNERModel()
    
    # Load sample contract
    contracts_dir = Path('data/raw/full_contract_txt')
    sample_files = list(contracts_dir.glob('*.txt'))[:3]
    
    if not sample_files:
        print("No contract files found in data/raw/full_contract_txt/")
        return
    
    for contract_file in sample_files:
        print(f"\n{'='*70}")
        print(f"Processing: {contract_file.name}")
        print(f"{'='*70}\n")
        
        # Read contract
        with open(contract_file, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        
        # Extract entities
        logger.info(f"Extracting entities from {contract_file.name}...")
        entities = model.extract_entities(text)
        
        # Display results
        print(f"Found {len(entities)} entities:\n")
        
        # Group by entity type
        summary = model.get_summary(entities)
        
        for label, count in sorted(summary.items()):
            print(f"{label}: {count} entities")
            
            # Show examples
            examples = [e for e in entities if e['label'] == label][:3]
            for ex in examples:
                print(f"  - {ex['text']} (confidence: {ex['confidence']:.2f})")
            print()
        
        # Show first few entities
        print("\nFirst 10 entities in document order:")
        print("-" * 70)
        for i, entity in enumerate(entities[:10], 1):
            print(f"{i}. [{entity['label']}] {entity['text'][:50]}... "
                  f"(pos: {entity['start']}-{entity['end']})")
        
        print()
    
    print("\n" + "="*70)
    print("Demo completed successfully!")
    print("="*70)


if __name__ == "__main__":
    demo_baseline_ner()
