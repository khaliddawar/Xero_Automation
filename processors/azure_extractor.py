from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from typing import Dict, Any, Optional
import os
from datetime import datetime

class AzureExtractor:
    def __init__(self):
        """Initialize Azure Form Recognizer client"""
        endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
        key = os.getenv("AZURE_FORM_RECOGNIZER_KEY")
        
        if not endpoint or not key:
            raise ValueError("Azure Form Recognizer credentials not found in environment variables")
            
        self.client = DocumentAnalysisClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )

    def process_document(self, content: bytes) -> Dict[str, Any]:
        """Process document using Azure Form Recognizer"""
        try:
            print("Processing document with Azure Form Recognizer...")
            
            # Start the analysis with prebuilt invoice model
            poller = self.client.begin_analyze_document(
                "prebuilt-invoice", 
                document=content
            )
            
            # Get results
            result = poller.result()
            
            # Process each invoice (usually just one)
            if result.documents:
                invoice = result.documents[0]
                
                # Extract key fields
                extracted_data = {
                    'vendor_info': self._extract_vendor_info(invoice),
                    'invoice_info': self._extract_invoice_info(invoice),
                    'amounts': self._extract_amounts(invoice),
                    'line_items': self._extract_line_items(invoice),
                    'confidence': invoice.confidence,
                    'text': result.content
                }
                
                print("\nExtraction Results:")
                print(f"Vendor: {extracted_data['vendor_info'].get('name', 'Not found')}")
                print(f"Invoice #: {extracted_data['invoice_info'].get('number', 'Not found')}")
                print(f"Total: ${extracted_data['amounts'].get('total', 0):.2f}")
                print(f"Confidence: {extracted_data['confidence'] * 100:.2f}%")
                
                return extracted_data
            else:
                print("No invoice data found in document")
                return None
                
        except Exception as e:
            print(f"Error processing document: {str(e)}")
            raise

    def _extract_vendor_info(self, invoice) -> Dict[str, Optional[str]]:
        """Extract vendor information"""
        vendor_info = {
            'name': None,
            'address': None,
            'tax_id': None,
            'phone': None,
            'email': None
        }
        
        try:
            fields = invoice.fields
            
            # Extract vendor name
            if 'VendorName' in fields:
                vendor_info['name'] = fields['VendorName'].value
                
            # Extract vendor address
            if 'VendorAddress' in fields:
                vendor_info['address'] = fields['VendorAddress'].value
                
            # Extract other vendor details
            if 'VendorTaxId' in fields:
                vendor_info['tax_id'] = fields['VendorTaxId'].value
                
            if 'VendorPhoneNumber' in fields:
                vendor_info['phone'] = fields['VendorPhoneNumber'].value
                
            if 'VendorEmail' in fields:
                vendor_info['email'] = fields['VendorEmail'].value
                
        except Exception as e:
            print(f"Error extracting vendor info: {str(e)}")
            
        return vendor_info

    def _extract_invoice_info(self, invoice) -> Dict[str, Optional[str]]:
        """Extract invoice details"""
        invoice_info = {
            'number': None,
            'date': None,
            'due_date': None,
            'purchase_order': None
        }
        
        try:
            fields = invoice.fields
            
            # Extract invoice number
            if 'InvoiceId' in fields:
                invoice_info['number'] = fields['InvoiceId'].value
                
            # Extract dates
            if 'InvoiceDate' in fields:
                date_val = fields['InvoiceDate'].value
                if isinstance(date_val, datetime):
                    invoice_info['date'] = date_val.strftime('%Y-%m-%d')
                    
            if 'DueDate' in fields:
                due_date_val = fields['DueDate'].value
                if isinstance(due_date_val, datetime):
                    invoice_info['due_date'] = due_date_val.strftime('%Y-%m-%d')
                    
            # Extract PO number
            if 'PurchaseOrder' in fields:
                invoice_info['purchase_order'] = fields['PurchaseOrder'].value
                
        except Exception as e:
            print(f"Error extracting invoice info: {str(e)}")
            
        return invoice_info

    def _extract_amounts(self, invoice) -> Dict[str, float]:
        """Extract monetary amounts"""
        amounts = {
            'subtotal': 0.0,
            'tax': 0.0,
            'total': 0.0
        }
        
        try:
            fields = invoice.fields
            
            # Extract amounts
            if 'SubTotal' in fields:
                amounts['subtotal'] = float(fields['SubTotal'].value)
                
            if 'TotalTax' in fields:
                amounts['tax'] = float(fields['TotalTax'].value)
                
            if 'InvoiceTotal' in fields:
                amounts['total'] = float(fields['InvoiceTotal'].value)
                
        except Exception as e:
            print(f"Error extracting amounts: {str(e)}")
            
        return amounts

    def _extract_line_items(self, invoice) -> List[Dict[str, Any]]:
        """Extract line items from invoice"""
        line_items = []
        
        try:
            if 'Items' in invoice.fields:
                items = invoice.fields['Items'].value
                for item in items:
                    line_item = {
                        'description': item.value.get('Description', {}).value,
                        'quantity': float(item.value.get('Quantity', {}).value or 0),
                        'unit_price': float(item.value.get('UnitPrice', {}).value or 0),
                        'amount': float(item.value.get('Amount', {}).value or 0)
                    }
                    line_items.append(line_item)
                    
        except Exception as e:
            print(f"Error extracting line items: {str(e)}")
            
        return line_items