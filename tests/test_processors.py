import pytest
from processors.ocr import OCRProcessor
from processors.text_analyzer import TextAnalyzer
from models.document import Document
from datetime import datetime
import os

@pytest.fixture
def sample_text():
    return """
    INVOICE
    Invoice #: INV-2024-001
    Date: 2024-01-15
    
    To:
    Acme Corp
    123 Business St
    Business City, 12345
    
    Amount: $1,234.56
    
    Please pay within 30 days.
    Contact: accounting@acmecorp.com
    Phone: +1 (555) 123-4567
    """

@pytest.fixture
def sample_document(sample_text):
    return Document(
        id="test-doc-001",
        source="test",
        content_type="text",
        raw_content=sample_text.encode(),
        processed_content={},
        created_at=datetime.now()
    )

def test_text_analyzer(sample_text):
    analyzer = TextAnalyzer()
    results = analyzer.process_text(sample_text)
    
    assert results is not None
    assert 'patterns' in results
    assert 'amount' in results['patterns']
    assert '$1,234.56' in results['patterns']['amount']
    assert 'INV-2024-001' in results['patterns']['invoice_number']

def test_document_creation(sample_document):
    assert sample_document.id == "test-doc-001"
    assert sample_document.source == "test"
    assert sample_document.content_type == "text"
    
    dict_form = sample_document.to_dict()
    assert dict_form['id'] == sample_document.id
    assert dict_form['source'] == sample_document.source