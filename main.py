from fastapi import FastAPI, HTTPException, BackgroundTasks
from input_handlers.email_handler import EmailHandler
from input_handlers.message_handler import get_message_handler
from processors.ocr import OCRProcessor
from processors.text_analyzer import TextAnalyzer
from integration.xero.xero_client import XeroClient
from models.document import Document
from typing import Dict, Any
import uvicorn
import uuid
from datetime import datetime

app = FastAPI(title="Xero Automation Service")

# Initialize processors
ocr_processor = OCRProcessor()
text_analyzer = TextAnalyzer()
xero_client = XeroClient()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        xero_client.authenticate()
    except Exception as e:
        print(f"Failed to initialize Xero client: {str(e)}")

@app.post("/process/email")
async def process_email(background_tasks: BackgroundTasks):
    """Process unread emails"""
    try:
        with EmailHandler() as email_handler:
            messages = email_handler.get_unread_messages()
            
        for message in messages:
            doc_id = str(uuid.uuid4())
            document = Document(
                id=doc_id,
                source='email',
                content_type='email',
                raw_content=str(message).encode(),
                processed_content={},
                created_at=datetime.now()
            )
            background_tasks.add_task(process_document, document)
            
        return {"status": "processing", "message_count": len(messages)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/message")
async def process_message(message: Dict[str, Any], background_tasks: BackgroundTasks):
    """Process incoming message (WhatsApp/ClickUp)"""
    try:
        handler = get_message_handler(message.get('source', ''))
        processed_message = handler.process_message(message)
        
        doc_id = str(uuid.uuid4())
        document = Document(
            id=doc_id,
            source=message.get('source', 'unknown'),
            content_type='message',
            raw_content=str(processed_message).encode(),
            processed_content={},
            created_at=datetime.now()
        )
        
        background_tasks.add_task(process_document, document)
        return {"status": "processing", "document_id": doc_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_document(document: Document):
    """Process document and update Xero"""
    try:
        # Extract text using OCR if needed
        if document.content_type in ['pdf', 'image']:
            ocr_results = ocr_processor.process_image(document.raw_content)
            text = ocr_results['text']
        else:
            text = document.raw_content.decode()
        
        # Analyze text
        analysis_results = text_analyzer.process_text(text)
        document.processed_content = analysis_results
        document.processed_at = datetime.now()
        
        # Create invoice in Xero if applicable
        if 'financial_data' in analysis_results:
            invoice_data = {
                'vendor_name': analysis_results.get('entities', {}).get('ORG', ['Unknown'])[0],
                'line_items': [{
                    'description': 'Invoice item',
                    'unit_amount': float(analysis_results['financial_data']['highest_amount'])
                }],
                'reference': analysis_results['patterns'].get('invoice_number', [''])[0]
            }
            xero_client.create_invoice(invoice_data)
            
    except Exception as e:
        print(f"Error processing document {document.id}: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)