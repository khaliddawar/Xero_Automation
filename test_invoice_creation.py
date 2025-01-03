from processors.ocr import OCRProcessor
from processors.text_analyzer import TextAnalyzer
from integration.xero.xero_client import XeroClient
from utils.logger import app_logger
from datetime import datetime, timedelta
import os

class InvoiceProcessor:
    def __init__(self):
        self.ocr_processor = OCRProcessor()
        self.text_analyzer = TextAnalyzer()
        self.xero_client = XeroClient()
        
    def extract_invoice_data(self, text_analysis):
        """Extract relevant invoice data from analysis results"""
        data = {
            'invoice_number': None,
            'amount': None,
            'date': None,
            'due_date': None,
            'vendor_name': None
        }
        
        patterns = text_analysis.get('patterns', {})
        entities = text_analysis.get('entities', {})
        
        # Get invoice number
        invoice_numbers = patterns.get('invoice_number', [])
        if invoice_numbers:
            data['invoice_number'] = invoice_numbers[0]
            
        # Get amount
        amounts = patterns.get('amount', [])
        if amounts:
            # Convert amount string to float
            amount_str = amounts[0].replace('$', '').replace(',', '')
            try:
                data['amount'] = float(amount_str)
            except ValueError:
                print(f"Could not convert amount: {amounts[0]}")
                
        # Get dates
        dates = patterns.get('date', [])
        if dates:
            data['date'] = dates[0]
            # Set due date to 30 days from invoice date if not found
            data['due_date'] = dates[1] if len(dates) > 1 else None
            
        # Get vendor name from entities
        organizations = entities.get('ORG', [])
        if organizations:
            data['vendor_name'] = organizations[0]
            
        return data
        
    def create_xero_invoice(self, invoice_data):
        """Create invoice in Xero"""
        try:
            # Prepare invoice data for Xero
            xero_invoice = {
                'Type': 'ACCPAY',  # Account Payable invoice
                'Contact': {
                    'Name': invoice_data.get('vendor_name', 'Unknown Vendor')
                },
                'LineItems': [{
                    'Description': f"Invoice {invoice_data.get('invoice_number', 'Unknown')}",
                    'Quantity': 1.0,
                    'UnitAmount': invoice_data.get('amount', 0.0),
                    'AccountCode': '200'  # Default expense account
                }],
                'Reference': invoice_data.get('invoice_number'),
                'Status': 'DRAFT'
            }
            
            # Add dates if available
            if invoice_data.get('date'):
                xero_invoice['Date'] = invoice_data['date']
            if invoice_data.get('due_date'):
                xero_invoice['DueDate'] = invoice_data['due_date']
                
            # Create invoice in Xero
            response = self.xero_client.create_invoice(xero_invoice)
            return response
            
        except Exception as e:
            print(f"Error creating Xero invoice: {str(e)}")
            raise

def main():
    processor = InvoiceProcessor()
    
    # Initialize Xero client
    print("Authenticating with Xero...")
    processor.xero_client.authenticate()
    
    # Process test files
    test_dir = "test_samples"
    if not os.path.exists(test_dir):
        print("Please place test invoice files in the 'test_samples' directory")
        return
        
    for filename in os.listdir(test_dir):
        if filename.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
            print(f"\nProcessing: {filename}")
            print("=" * 50)
            
            try:
                # Read file
                file_path = os.path.join(test_dir, filename)
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                    
                # Process file based on type
                if filename.lower().endswith('.pdf'):
                    ocr_results = processor.ocr_processor.process_pdf(file_content)
                else:
                    ocr_results = processor.ocr_processor.process_image(file_content)
                    
                # Analyze text
                analysis_results = processor.text_analyzer.process_text(ocr_results['text'])
                
                # Extract invoice data
                invoice_data = processor.extract_invoice_data(analysis_results)
                print("\nExtracted Invoice Data:")
                for key, value in invoice_data.items():
                    print(f"{key}: {value}")
                    
                # Create invoice in Xero
                if invoice_data['amount'] and invoice_data['invoice_number']:
                    print("\nCreating invoice in Xero...")
                    xero_response = processor.create_xero_invoice(invoice_data)
                    print("✓ Invoice created successfully in Xero!")
                    print(f"Xero Invoice ID: {xero_response.get('InvoiceID')}")
                else:
                    print("\n❌ Insufficient data to create invoice")
                    
            except Exception as e:
                print(f"\n❌ Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    main()