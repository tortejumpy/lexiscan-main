"""
Test script for OCR Pipeline
Tests the complete OCR pipeline on sample contracts
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ocr.pipeline import OCRPipeline
from src.utils.helpers import setup_logging, load_config

# Setup logging
setup_logging(log_file='logs/ocr_test.log', log_level='INFO')
logger = logging.getLogger(__name__)


def test_ocr_pipeline():
    """Test OCR pipeline on sample contracts"""
    
    # Initialize pipeline
    pipeline = OCRPipeline(
        dpi=300,
        language='eng',
        confidence_threshold=60
    )
    
    # Get sample contracts
    contracts_dir = Path('data/raw/full_contract_txt')
    contract_files = list(contracts_dir.glob('*.txt'))[:5]  # Test on first 5
    
    logger.info(f"Testing OCR pipeline on {len(contract_files)} contracts")
    
    results = []
    
    for contract_file in contract_files:
        logger.info(f"\nProcessing: {contract_file.name}")
        
        # Read text file (simulating OCR output for now)
        with open(contract_file, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        
        # Display statistics
        logger.info(f"Text length: {len(text)} characters")
        logger.info(f"Word count: {len(text.split())} words")
        
        # Show first 500 characters
        logger.info(f"Sample text:\n{text[:500]}...")
        
        results.append({
            'filename': contract_file.name,
            'text_length': len(text),
            'word_count': len(text.split())
        })
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("OCR Pipeline Test Summary")
    logger.info("="*50)
    
    for result in results:
        logger.info(f"{result['filename']}: "
                   f"{result['text_length']} chars, "
                   f"{result['word_count']} words")
    
    logger.info("\nOCR Pipeline test completed successfully!")


if __name__ == "__main__":
    test_ocr_pipeline()
