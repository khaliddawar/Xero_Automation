import os
from processors.text_analyzer import TextAnalyzer
from processors.ocr import OCRProcessor
from input_handlers.email_handler import EmailHandler
from input_handlers.message_handler import WhatsAppHandler, ClickUpHandler
from utils.logger import app_logger
from models.document import Document
from datetime import datetime

def test_text_analyzer():
    """Test the text analysis component"""
    analyzer = TextAnalyzer()
    
    # Test sample invoice text
    sample_text = """
    INVOICE
    Invoice #: INV-2024-001
    Date: 2024-01-15
    Amount: $1,234.56
    
    From: Test Company Ltd
    Email: billing@testcompany.com
    Phone: +1 (555) 123-4567
    """
    
    app_logger.info("Testing text analyzer...")
    results = analyzer.process_text(sample_text)
    
    print("\nText Analysis Results:")
    print(f"Found amounts: {results.get('patterns', {}).get('amount', [])}")
    print(f"Found invoice numbers: {results.get('patterns', {}).get('invoice_number', [])}")
    print(f"Found entities: {results.get('entities', {})}")
    
    return results

def test_email_handler():
    """Test the email handler"""
    try:
        with EmailHandler() as handler:
            app_logger.info("Testing email connection...")
            # This will test the connection
            print("\nEmail Handler Test:")
            print("Successfully connected to email server")
            return True
    except Exception as e:
        print(f"Email connection failed: {str(e)}")
        return False

def test_document_creation():
    """Test document model"""
    doc = Document(
        id="test-001",
        source="test",
        content_type="text",
        raw_content=b"Test content",
        processed_content={},
        created_at=datetime.now()
    )
    
    print("\nDocument Creation Test:")
    print(f"Document ID: {doc.id}")
    print(f"Created at: {doc.created_at}")
    return doc

def main():
    """Run all tests"""
    print("Starting system tests...\n")
    
    # Test 1: Text Analysis
    print("=== Text Analysis Test ===")
    text_results = test_text_analyzer()
    
    # Test 2: Email Handler
    print("\n=== Email Handler Test ===")
    email_result = test_email_handler()
    
    # Test 3: Document Creation
    print("\n=== Document Creation Test ===")
    doc_result = test_document_creation()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main()