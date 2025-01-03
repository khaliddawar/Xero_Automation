import cv2
import numpy as np
from typing import Dict, Any, List, Tuple
import pytesseract
from pdf2image import convert_from_bytes
import tempfile

class AdvancedOCR:
    def __init__(self):
        """Initialize with optimized configurations"""
        self.zones = {
            'header': (0, 0.3),    # Top 30% - vendor info, invoice number
            'body': (0.2, 0.8),    # Middle - line items
            'footer': (0.7, 1.0)   # Bottom - totals
        }
        
        self.ocr_configs = {
            'header': '--oem 3 --psm 1',  # Automatic page segmentation
            'detail': '--oem 3 --psm 6',  # Uniform block of text
            'numbers': '--oem 3 --psm 7'  # Single line of text
        }

    def enhance_image(self, image: np.ndarray) -> List[np.ndarray]:
        """Apply multiple enhancement techniques"""
        enhanced = []
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Advanced noise removal
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        contrast_enhanced = clahe.apply(denoised)
        
        # Multiple threshold versions
        _, binary = cv2.threshold(contrast_enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        adaptive = cv2.adaptiveThreshold(contrast_enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        enhanced.extend([gray, contrast_enhanced, binary, adaptive])
        return enhanced

    def extract_zone(self, image: np.ndarray, zone: str) -> np.ndarray:
        """Extract a specific zone from the image"""
        height, width = image.shape[:2]
        start, end = self.zones[zone]
        return image[int(height * start):int(height * end), :]

    def process_zone(self, image: np.ndarray, zone_name: str) -> Dict[str, Any]:
        """Process a specific zone with optimized settings"""
        results = []
        confidence_scores = []
        
        # Extract zone
        zone_image = self.extract_zone(image, zone_name)
        
        # Get enhanced versions
        enhanced_images = self.enhance_image(zone_image)
        
        # Process each enhanced version
        for img in enhanced_images:
            try:
                # OCR with zone-specific config
                data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, 
                                               config=self.ocr_configs.get(zone_name, self.ocr_configs['detail']))
                
                # Calculate confidence
                confidences = [float(conf) for conf in data['conf'] if conf != '-1']
                if confidences:
                    avg_confidence = sum(confidences) / len(confidences)
                    text = pytesseract.image_to_string(img)
                    
                    results.append(text)
                    confidence_scores.append(avg_confidence)
            except Exception as e:
                print(f"Error processing {zone_name} zone: {str(e)}")
                continue
        
        # Return best result
        if results:
            best_idx = confidence_scores.index(max(confidence_scores))
            return {
                'text': results[best_idx],
                'confidence': confidence_scores[best_idx],
                'zone': zone_name
            }
        return {'text': '', 'confidence': 0, 'zone': zone_name}

    def process_image(self, image_data: bytes) -> Dict[str, Any]:
        """Process entire image with zone-based approach"""
        try:
            # Convert bytes to image
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Failed to decode image")
            
            # Process each zone
            results = {}
            for zone in self.zones.keys():
                results[zone] = self.process_zone(image, zone)
            
            # Combine results
            combined_text = '\n'.join(zone['text'] for zone in results.values())
            avg_confidence = sum(zone['confidence'] for zone in results.values()) / len(results)
            
            return {
                'text': combined_text,
                'confidence': avg_confidence,
                'zones': results
            }
        
        except Exception as e:
            raise RuntimeError(f"Image processing failed: {str(e)}")

    def process_pdf(self, pdf_data: bytes) -> Dict[str, Any]:
        """Process PDF with optimized settings"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Convert PDF to high-resolution images
                images = convert_from_bytes(pdf_data, dpi=400)
                
                all_results = []
                for i, image in enumerate(images):
                    # Convert PIL image to OpenCV format
                    opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                    
                    # Process image
                    result = self.process_image(cv2.imencode('.png', opencv_image)[1].tobytes())
                    result['page'] = i + 1
                    all_results.append(result)
                
                # Find best quality page
                best_result = max(all_results, key=lambda x: x['confidence'])
                
                return {
                    'best_result': best_result,
                    'all_results': all_results,
                    'page_count': len(images)
                }
                
        except Exception as e:
            raise RuntimeError(f"PDF processing failed: {str(e)}")
