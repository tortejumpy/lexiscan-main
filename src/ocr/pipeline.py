"""
Complete OCR Pipeline for LexiScan Auto
Orchestrates PDF processing, OCR, and text cleaning
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from .pdf_processor import PDFProcessor
from .ocr_engine import OCREngine
from .text_cleaner import TextCleaner

logger = logging.getLogger(__name__)


@dataclass
class OCRResult:
    """Container for OCR processing results"""
    text: str
    confidence: float
    num_pages: int
    is_scanned: bool
    quality_metrics: Dict[str, float]
    processing_time: float


class OCRPipeline:
    """
    Complete OCR pipeline for processing legal contracts
    """
    
    def __init__(
        self,
        dpi: int = 300,
        language: str = 'eng',
        confidence_threshold: int = 60,
        tesseract_cmd: Optional[str] = None
    ):
        """
        Initialize OCR pipeline
        
        Args:
            dpi: Resolution for PDF to image conversion
            language: OCR language code
            confidence_threshold: Minimum OCR confidence
            tesseract_cmd: Path to tesseract executable
        """
        self.pdf_processor = PDFProcessor(dpi=dpi)
        self.ocr_engine = OCREngine(
            language=language,
            confidence_threshold=confidence_threshold,
            tesseract_cmd=tesseract_cmd
        )
        self.text_cleaner = TextCleaner()
        
        logger.info("OCR Pipeline initialized")
    
    def process_document(
        self,
        pdf_path: str,
        output_dir: Optional[str] = None,
        clean_text: bool = True
    ) -> OCRResult:
        """
        Process a PDF document through the complete OCR pipeline
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory for intermediate files
            clean_text: Apply text cleaning
            
        Returns:
            OCRResult object with extracted text and metadata
        """
        import time
        start_time = time.time()
        
        pdf_path = Path(pdf_path)
        logger.info(f"Processing document: {pdf_path.name}")
        
        # Check if PDF is scanned or text-based
        is_scanned = self.pdf_processor.is_scanned_pdf(str(pdf_path))
        
        if is_scanned:
            logger.info("Document is scanned - using OCR")
            text, confidence, metrics = self._process_scanned_pdf(
                str(pdf_path),
                output_dir
            )
        else:
            logger.info("Document contains text - extracting directly")
            text = self.pdf_processor.extract_text_from_pdf(str(pdf_path))
            confidence = 100.0
            metrics = {}
        
        # Clean text if requested
        if clean_text and text:
            text = self.text_cleaner.clean_text(text)
        
        # Get PDF info
        pdf_info = self.pdf_processor.get_pdf_info(str(pdf_path))
        num_pages = pdf_info.get('num_pages', 0)
        
        processing_time = time.time() - start_time
        
        result = OCRResult(
            text=text,
            confidence=confidence,
            num_pages=num_pages,
            is_scanned=is_scanned,
            quality_metrics=metrics,
            processing_time=processing_time
        )
        
        logger.info(f"Processing completed in {processing_time:.2f}s "
                   f"(confidence: {confidence:.2f}%)")
        
        return result
    
    def _process_scanned_pdf(
        self,
        pdf_path: str,
        output_dir: Optional[str] = None
    ) -> Tuple[str, float, Dict]:
        """
        Process scanned PDF through OCR
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory for images
            
        Returns:
            Tuple of (text, confidence, metrics)
        """
        # Convert PDF to images
        image_paths = self.pdf_processor.pdf_to_images(
            pdf_path,
            output_dir=output_dir
        )
        
        # Extract text from images
        text = self.ocr_engine.extract_from_multiple_images(
            image_paths,
            preprocess=True
        )
        
        # Calculate quality metrics from first page
        metrics = {}
        if image_paths:
            metrics = self.ocr_engine.get_ocr_quality_metrics(image_paths[0])
        
        confidence = metrics.get('avg_confidence', 0.0)
        
        return text, confidence, metrics
    
    def process_batch(
        self,
        pdf_paths: List[str],
        output_dir: Optional[str] = None
    ) -> List[OCRResult]:
        """
        Process multiple PDF documents
        
        Args:
            pdf_paths: List of PDF file paths
            output_dir: Directory for intermediate files
            
        Returns:
            List of OCRResult objects
        """
        results = []
        
        logger.info(f"Processing batch of {len(pdf_paths)} documents")
        
        for i, pdf_path in enumerate(pdf_paths, 1):
            try:
                logger.info(f"Processing document {i}/{len(pdf_paths)}")
                result = self.process_document(pdf_path, output_dir)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing {pdf_path}: {str(e)}")
                # Create empty result for failed document
                results.append(OCRResult(
                    text="",
                    confidence=0.0,
                    num_pages=0,
                    is_scanned=True,
                    quality_metrics={},
                    processing_time=0.0
                ))
        
        logger.info(f"Batch processing completed: {len(results)} documents")
        
        return results
    
    def save_extracted_text(
        self,
        result: OCRResult,
        output_path: str
    ) -> None:
        """
        Save extracted text to file
        
        Args:
            result: OCRResult object
            output_path: Path to save text file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result.text)
        
        logger.info(f"Saved extracted text to {output_path}")
