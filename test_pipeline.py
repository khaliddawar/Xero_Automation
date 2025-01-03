import os
from processors.ocr import OCRProcessor
from processors.text_analyzer import TextAnalyzer
from models.document import Document
from datetime import datetime
from utils.logger import app_logger
import uuid

class PipelineTester:
    def __init__(self):
        self.ocr_processor = OCRProcessor()
        self.text_analyzer = TextAnalyzer()
        
    def test_full_pipeline(self, file_path):
        try:
            # Step 1: Create a document
            doc_id = str(uuid.uuid4())
            print(f"\n1. Creating document with ID: {doc_id}")
            
            with open(file_path, 'rb') as f:
                file_content = f.read()
                
            # Determine file type
            file_ext = os.path.splitext(file_path)[1].lower()
            content_type = 'pdf' if file_ext == '.pdf' else 'image'
            
            document = Document(
                id=doc_id,
                source="test",
                content_type=content_type,
                raw_content=file_content,
                processed_content={},
                created_at=datetime.now()
            )
            print("✓ Document created successfully")

            # Step 2: OCR Processing
            print(f"\n2. Performing OCR processing on {content_type}...")
            if content_type == 'pdf':
                ocr_results = self.ocr_processor.process_pdf(document.raw_content)
            else:
                ocr_results = self.ocr_processor.process_image(document.raw_content)
                
            print(f"✓ OCR completed with confidence: {ocr_results.get('confidence', 0):.2f}%")
            print("\nExtracted text sample:")
            print("-" * 50)
            print(ocr_results['text'][:500] + "..." if len(ocr_results['text']) > 500 else ocr_results['text'])
            print("-" * 50)

            # Step 3: Text Analysis
            print("\n3. Analyzing extracted text...")
            analysis_results = self.text_analyzer.process_text(ocr_results['text'])
            
            # Print analysis results
            print("\nAnalysis Results:")
            print("-" * 50)
            if 'patterns' in analysis_results:
                patterns = analysis_results['patterns']
                print(f"Found amounts: {patterns.get('amount', [])}")
                print(f"Found invoice numbers: {patterns.get('invoice_number', [])}")
                print(f"Found dates: {patterns.get('date', [])}")
            
            if 'entities' in analysis_results:
                print(f"\nEntities found: {analysis_results['entities']}")
            print("-" * 50)

            # Update document with processed results
            document.processed_content = {
                'ocr_results': ocr_results,
                'analysis_results': analysis_results
            }
            document.processed_at = datetime.now()

            return {
                'status': 'success',
                'document_id': doc_id,
                'results': document.processed_content
            }

        except Exception as e:
            print(f"\n❌ Error in pipeline: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }

def main():
    tester = PipelineTester()
    
    # Check for test samples
    test_dir = "test_samples"
    if not os.path.exists(test_dir):
        print("Please place test invoice images in the 'test_samples' directory")
        return

    # Process all images in test directory
    for filename in os.listdir(test_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
            print(f"\nProcessing: {filename}")
            print("=" * 50)
            
            file_path = os.path.join(test_dir, filename)
            results = tester.test_full_pipeline(file_path)
            
            if results['status'] == 'success':
                print("\n✓ Pipeline test completed successfully!")
            else:
                print(f"\n❌ Pipeline test failed: {results.get('error')}")

if __name__ == "__main__":
    main()