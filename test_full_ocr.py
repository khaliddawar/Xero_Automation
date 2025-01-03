import pytesseract
from PIL import Image
import os
from utils.config import config

def test_full_ocr():
    # Set Tesseract path
    pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH
    
    try:
        # First verify Tesseract is working
        version = pytesseract.get_tesseract_version()
        print(f"Tesseract version: {version}")
        print(f"Using Tesseract from: {config.TESSERACT_PATH}")
        
        # Create a simple test image with text (if you don't have one)
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a new image with white background
        img = Image.new('RGB', (400, 100), color='white')
        d = ImageDraw.Draw(img)
        
        # Add text to image
        d.text((10,10), "Testing OCR 123", fill='black')
        
        # Save the test image
        test_image_path = "test_ocr_image.png"
        img.save(test_image_path)
        
        # Perform OCR on the test image
        print("\nPerforming OCR on test image...")
        text = pytesseract.image_to_string(Image.open(test_image_path))
        print(f"Extracted text: {text.strip()}")
        
        # Clean up
        os.remove(test_image_path)
        
        print("\nOCR test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during OCR test: {str(e)}")
        print("\nDebug information:")
        print(f"Python version: {pytesseract.sys.version}")
        return False

if __name__ == "__main__":
    test_full_ocr()