import pytesseract
import cv2
import numpy as np
from typing import Dict, Any, Optional, List
from pathlib import Path
import io
from utils.config import config
from pdf2image import convert_from_bytes
import tempfile
import os
import logging

class OCRProcessor:
    def __init__(self):
        # Set Tesseract executable path from config
        pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH
        # Set Poppler path
        self.poppler_path = r'C:\Program Files\poppler-24.08.0\Library\bin'
        
        # Define OCR configs for different attempts
        self.ocr_configs = [
            '--oem 3 --psm 6',  # Assume uniform block of text
            '--oem 3 --psm 3',  # Fully automatic page segmentation
            '--oem 3 --psm 4',  # Assume single column of text
            '--oem 3 --psm 1'   # Automatic page segmentation with OSD
        ]
        
    def _enhance_image(self, image: np.ndarray) -> List[np.ndarray]:
        """Apply different image enhancement techniques"""
        enhanced_images = []
        
        # Original grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        enhanced_images.append(gray)
        
        # Otsu's thresholding
        _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        enhanced_images.append(otsu)
        
        # Adaptive Gaussian thresholding
        adaptive = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        enhanced_images.append(adaptive)
        
        # Contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced_contrast = clahe.apply(gray)
        enhanced_images.append(enhanced_contrast)
        
        return enhanced_images

    def _remove_noise(self, image: np.ndarray) -> np.ndarray:
        """Remove noise from image"""
        # Apply bilateral filter to remove noise while preserving edges
        denoised = cv2.bilateralFilter(image, 9, 75, 75)
        return denoised

    def _deskew(self, image: np.ndarray) -> np.ndarray:
        """Deskew image if needed"""
        try:
            # Calculate skew angle
            coords = np.column_stack(np.where(image > 0))
            angle = cv2.minAreaRect(coords)[-1]
            
            if angle < -45:
                angle = 90 + angle
            
            # Rotate image if skew is detected
            if abs(angle) > 0.5:
                (h, w) = image.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(
                    image, M, (w, h),
                    flags=cv2.INTER_CUBIC,
                    borderMode=cv2.BORDER_REPLICATE
                )
                return rotated
                
        except Exception as e:
            print(f"Deskew failed: {str(e)}")
            
        return image

    def _process_single_image(self, image: np.ndarray) -> Dict[str, Any]:
        """Process a single image with multiple enhancement attempts"""
        best_result = None
        highest_confidence = 0
        
        try:
            # Remove noise
            denoised = self._remove_noise(image)
            
            # Get enhanced versions
            enhanced_images = self._enhance_image(denoised)
            
            # Try each enhancement with each OCR config
            for enhanced in enhanced_images:
                # Deskew the enhanced image
                deskewed = self._deskew(enhanced)
                
                for config in self.ocr_configs:
                    try:
                        # Perform OCR
                        text = pytesseract.image_to_string(deskewed, config=config)
                        data = pytesseract.image_to_data(deskewed, output_type=pytesseract.Output.DICT)
                        
                        # Calculate confidence
                        confidences = [int(conf) for conf in data['conf'] if conf != '-1']
                        if not confidences:
                            continue
                            
                        avg_confidence = sum(confidences) / len(confidences)
                        
                        # Check if this is the best result so far
                        if avg_confidence > highest_confidence:
                            result = {
                                'text': text,
                                'confidence': avg_confidence,
                                'word_count': len(text.split()),
                                'details': data
                            }
                            
                            # Check if the result contains key invoice elements
                            key_words = ['invoice', 'total', 'amount', 'date', 'payment']
                            if any(word.lower() in text.lower() for word in key_words):
                                # Give preference to results with invoice-related content
                                avg_confidence += 10
                                
                            if avg_confidence > highest_confidence:
                                highest_confidence = avg_confidence
                                best_result = result
                    
                    except Exception as e:
                        print(f"OCR attempt failed with config {config}: {str(e)}")
                        continue
            
            if best_result is None:
                raise ValueError("All OCR attempts failed")
                
            return best_result
            
        except Exception as e:
            raise RuntimeError(f"Image processing failed: {str(e)}")

    def process_image(self, image_data: bytes) -> Dict[str, Any]:
        """Process image data and extract text using OCR"""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Failed to decode image data")
            
            return self._process_single_image(image)
            
        except Exception as e:
            raise RuntimeError(f"OCR processing failed: {str(e)}")
    
    def process_pdf(self, pdf_data: bytes) -> Dict[str, Any]:
        """Process PDF file and extract text using OCR"""
        try:
            print(f"Using Poppler path: {self.poppler_path}")
            
            # Create a temporary directory for PDF processing
            with tempfile.TemporaryDirectory() as temp_dir:
                print("Converting PDF to images...")
                # Convert PDF to images with higher DPI
                images = convert_from_bytes(
                    pdf_data,
                    dpi=400,  # Increased DPI for better quality
                    poppler_path=self.poppler_path
                )
                print(f"Converted PDF to {len(images)} images")
                
                # Process each page
                all_text = []
                total_confidence = 0
                total_words = 0
                best_page_result = None
                highest_page_confidence = 0
                
                for i, image in enumerate(images, 1):
                    print(f"Processing page {i} of {len(images)}...")
                    # Convert PIL Image to OpenCV format
                    opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                    
                    # Process the page
                    page_result = self._process_single_image(opencv_image)
                    
                    # Track the best page result (usually the first page has the invoice details)
                    if page_result['confidence'] > highest_page_confidence:
                        highest_page_confidence = page_result['confidence']
                        best_page_result = page_result
                    
                    all_text.append(f"=== Page {i} ===\n{page_result['text']}")
                    total_confidence += page_result['confidence']
                    total_words += page_result['word_count']
                
                # Combine results, but use the best page's text first
                if best_page_result:
                    all_text.insert(0, best_page_result['text'])
                
                # Calculate average confidence
                avg_confidence = total_confidence / len(images) if images else 0
                
                return {
                    'text': '\n\n'.join(all_text),
                    'confidence': avg_confidence,
                    'word_count': total_words,
                    'page_count': len(images),
                    'best_page': best_page_result,
                    'metadata': {
                        'pages': len(images),
                        'dpi': 400
                    }
                }
                
        except Exception as e:
            print(f"Detailed error in process_pdf: {str(e)}")
            raise RuntimeError(f"PDF processing failed: {str(e)}")