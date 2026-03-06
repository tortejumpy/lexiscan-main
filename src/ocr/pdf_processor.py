"""
PDF to Image Converter for OCR Pipeline
"""

import os
import logging
from pathlib import Path
from typing import List, Optional, Tuple
from PIL import Image
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    Handles PDF to image conversion for OCR processing
    """
    
    def __init__(self, dpi: int = 300, output_format: str = "PNG"):
        """
        Initialize PDF processor
        
        Args:
            dpi: Resolution for image conversion
            output_format: Output image format (PNG, JPEG)
        """
        self.dpi = dpi
        self.output_format = output_format.upper()
        self.zoom = dpi / 72  # PDF default is 72 DPI
        
        logger.info(f"PDFProcessor initialized with DPI={dpi}, format={output_format}")
    
    def pdf_to_images(self, pdf_path: str, output_dir: Optional[str] = None) -> List[str]:
        """
        Convert PDF pages to images
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save images (optional)
            
        Returns:
            List of image file paths
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Setup output directory
        if output_dir is None:
            output_dir = pdf_path.parent / f"{pdf_path.stem}_images"
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        image_paths = []
        
        try:
            # Open PDF with PyMuPDF
            pdf_document = fitz.open(str(pdf_path))
            total_pages = len(pdf_document)
            
            logger.info(f"Processing {total_pages} pages from {pdf_path.name}")
            
            # Convert each page to image
            for page_num in range(total_pages):
                page = pdf_document[page_num]
                
                # Create transformation matrix for desired DPI
                mat = fitz.Matrix(self.zoom, self.zoom)
                
                # Render page to pixmap
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # Save image
                image_filename = f"page_{page_num + 1:04d}.{self.output_format.lower()}"
                image_path = output_dir / image_filename
                
                pix.save(str(image_path))
                image_paths.append(str(image_path))
                
                logger.debug(f"Converted page {page_num + 1}/{total_pages}")
            
            pdf_document.close()
            logger.info(f"Successfully converted {total_pages} pages to images")
            
        except Exception as e:
            logger.error(f"Error converting PDF to images: {str(e)}")
            raise
        
        return image_paths
    
    def get_pdf_info(self, pdf_path: str) -> dict:
        """
        Extract metadata from PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with PDF metadata
        """
        try:
            pdf_document = fitz.open(str(pdf_path))
            
            metadata = {
                'num_pages': len(pdf_document),
                'title': pdf_document.metadata.get('title', ''),
                'author': pdf_document.metadata.get('author', ''),
                'subject': pdf_document.metadata.get('subject', ''),
                'creator': pdf_document.metadata.get('creator', ''),
                'producer': pdf_document.metadata.get('producer', ''),
                'creation_date': pdf_document.metadata.get('creationDate', ''),
                'modification_date': pdf_document.metadata.get('modDate', ''),
            }
            
            pdf_document.close()
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting PDF metadata: {str(e)}")
            return {}
    
    def is_scanned_pdf(self, pdf_path: str, text_threshold: int = 50) -> bool:
        """
        Determine if PDF is scanned (image-based) or text-based
        
        Args:
            pdf_path: Path to PDF file
            text_threshold: Minimum characters to consider text-based
            
        Returns:
            True if scanned (image-based), False if text-based
        """
        try:
            pdf_document = fitz.open(str(pdf_path))
            
            # Check first few pages for text content
            pages_to_check = min(3, len(pdf_document))
            total_text_length = 0
            
            for page_num in range(pages_to_check):
                page = pdf_document[page_num]
                text = page.get_text()
                total_text_length += len(text.strip())
            
            pdf_document.close()
            
            # If very little text found, likely scanned
            is_scanned = total_text_length < text_threshold
            
            logger.info(f"PDF {'is scanned' if is_scanned else 'contains text'} "
                       f"(text length: {total_text_length})")
            
            return is_scanned
            
        except Exception as e:
            logger.error(f"Error checking PDF type: {str(e)}")
            return True  # Assume scanned if error
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text directly from text-based PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        try:
            pdf_document = fitz.open(str(pdf_path))
            text_content = []
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                text = page.get_text()
                text_content.append(text)
            
            pdf_document.close()
            
            full_text = "\n\n".join(text_content)
            logger.info(f"Extracted {len(full_text)} characters from PDF")
            
            return full_text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return ""
