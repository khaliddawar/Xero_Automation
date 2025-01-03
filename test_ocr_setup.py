import pytesseract
from utils.config import config
import sys

def test_tesseract_setup():
    try:
        # Explicitly set the tesseract command path
        pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH
        
        # Print Tesseract version
        version = pytesseract.get_tesseract_version()
        print(f"Tesseract version: {version}")
        print(f"Using Tesseract from: {config.TESSERACT_PATH}")
        print("Tesseract is working correctly!")
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nDebug information:")
        print(f"Attempted Tesseract path: {config.TESSERACT_PATH}")
        print(f"Python version: {sys.version}")
        print("\nPossible solutions:")
        print("1. Verify Tesseract is installed at the correct path")
        print("2. Check if the path in config.py matches your installation")
        print("3. Try restarting your terminal/IDE after PATH changes")
        return False

if __name__ == "__main__":
    test_tesseract_setup()