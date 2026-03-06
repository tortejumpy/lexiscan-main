"""
OCR Engine using Tesseract for text extraction from images
"""

import os
import logging
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import numpy as np

logger = logging.getLogger(__name__)


class OCREngine:
    """
    Tesseract OCR wrapper with preprocessing capabilities
    """
    
    def __init__(
        self,
        language: str = 'eng',
        confidence_threshold: int = 60,
        tesseract_cmd: Optional[str] = None
    ):
        """
        Initialize OCR engine
        
        Args:
            language: Tesseract language code
            confidence_threshold: Minimum confidence score (0-100)
            tesseract_cmd: Path to tesseract executable (optional)
        """
        self.language = language
        self.confidence_threshold = confidence_threshold
        
        # Set tesseract command path if provided
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        logger.info(f"OCREngine initialized with language={language}, "
                   f"confidence_threshold={confidence_threshold}")
    
    def preprocess_image(
        self,
        image: Image.Image,
        denoise: bool = True,
        enhance_contrast: bool = True,
        sharpen: bool = True
    ) -> Image.Image:
        """
        Preprocess image for better OCR accuracy
        
        Args:
            image: PIL Image object
            denoise: Apply denoising filter
            enhance_contrast: Enhance image contrast
            sharpen: Apply sharpening filter
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
        
        # Enhance contrast
        if enhance_contrast:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
        
        # Denoise
        if denoise:
            image = image.filter(ImageFilter.MedianFilter(size=3))
        
        # Sharpen
        if sharpen:
            image = image.filter(ImageFilter.SHARPEN)
        
        return image
    
    def extract_text(
        self,
        image_path: str,
        preprocess: bool = True,
        config: str = '--psm 1'
    ) -> str:
        """
        Extract text from image using OCR
        
        Args:
            image_path: Path to image file
            preprocess: Apply preprocessing
            config: Tesseract configuration string
            
        Returns:
            Extracted text
        """
        try:
            # Load image
            image = Image.open(image_path)
            
            # Preprocess if enabled
            if preprocess:
                image = self.preprocess_image(image)
            
            # Perform OCR
            text = pytesseract.image_to_string(
                image,
                lang=self.language,
                config=config
            )
            
            logger.debug(f"Extracted {len(text)} characters from {Path(image_path).name}")
            
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from {image_path}: {str(e)}")
            return ""
    
    def extract_text_with_confidence(
        self,
        image_path: str,
        preprocess: bool = True
    ) -> Tuple[str, float]:
        """
        Extract text with confidence scores
        
        Args:
            image_path: Path to image file
            preprocess: Apply preprocessing
            
        Returns:
            Tuple of (text, average_confidence)
        """
        try:
            # Load image
            image = Image.open(image_path)
            
            # Preprocess if enabled
            if preprocess:
                image = self.preprocess_image(image)
            
            # Get detailed OCR data
            data = pytesseract.image_to_data(
                image,
                lang=self.language,
                output_type=pytesseract.Output.DICT
            )
            
            # Filter by confidence threshold
            filtered_text = []
            confidences = []
            
            for i, conf in enumerate(data['conf']):
                if conf != -1 and conf >= self.confidence_threshold:
                    text = data['text'][i].strip()
                    if text:
                        filtered_text.append(text)
                        confidences.append(conf)
            
            # Calculate average confidence
            avg_confidence = np.mean(confidences) if confidences else 0.0
            
            # Reconstruct text
            full_text = ' '.join(filtered_text)
            
            logger.debug(f"Extracted text with avg confidence: {avg_confidence:.2f}%")
            
            return full_text, avg_confidence
            
        except Exception as e:
            logger.error(f"Error extracting text with confidence: {str(e)}")
            return "", 0.0
    
    def extract_from_multiple_images(
        self,
        image_paths: List[str],
        preprocess: bool = True
    ) -> str:
        """
        Extract text from multiple images (e.g., multi-page PDF)
        
        Args:
            image_paths: List of image file paths
            preprocess: Apply preprocessing
            
        Returns:
            Combined extracted text
        """
        all_text = []
        total_confidence = []
        
        logger.info(f"Processing {len(image_paths)} images")
        
        for i, image_path in enumerate(image_paths, 1):
            text, confidence = self.extract_text_with_confidence(
                image_path,
                preprocess=preprocess
            )
            
            if text:
                all_text.append(f"--- Page {i} ---\n{text}")
                total_confidence.append(confidence)
            
            logger.debug(f"Processed page {i}/{len(image_paths)}")
        
        # Calculate overall statistics
        avg_confidence = np.mean(total_confidence) if total_confidence else 0.0
        combined_text = "\n\n".join(all_text)
        
        logger.info(f"Extracted {len(combined_text)} characters with "
                   f"average confidence: {avg_confidence:.2f}%")
        
        return combined_text
    
    def get_ocr_quality_metrics(self, image_path: str) -> Dict[str, float]:
        """
        Calculate OCR quality metrics for an image
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with quality metrics
        """
        try:
            image = Image.open(image_path)
            image = self.preprocess_image(image)
            
            # Get detailed OCR data
            data = pytesseract.image_to_data(
                image,
                lang=self.language,
                output_type=pytesseract.Output.DICT
            )
            
            # Calculate metrics
            confidences = [c for c in data['conf'] if c != -1]
            
            metrics = {
                'avg_confidence': np.mean(confidences) if confidences else 0.0,
                'min_confidence': np.min(confidences) if confidences else 0.0,
                'max_confidence': np.max(confidences) if confidences else 0.0,
                'std_confidence': np.std(confidences) if confidences else 0.0,
                'total_words': len([t for t in data['text'] if t.strip()]),
                'low_confidence_words': sum(1 for c in confidences if c < self.confidence_threshold)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating OCR metrics: {str(e)}")
            return {}
