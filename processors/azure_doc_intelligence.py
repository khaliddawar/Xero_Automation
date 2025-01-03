from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from typing import Dict, Any, List, Optional
import os
from datetime import datetime
import logging
import re

class AzureDocProcessor:
    def __init__(self):
        endpoint = os.getenv("AZURE_DOC_INTELLIGENCE_ENDPOINT")
        key = os.getenv("AZURE_DOC_INTELLIGENCE_KEY")
        
        if not endpoint or not key:
            raise ValueError("Azure Document Intelligence credentials not found")
            
        self.client = DocumentAnalysisClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )
        
    def clean_text(self, text: str) -> str:
        """Clean text while preserving Arabic and English"""
        if not text:
            return ""
        # Remove excess whitespace while preserving Arabic
        text = re.sub(r'\s+', ' ', text)
        # Remove common artifacts
        text = text.replace('\n', ' ').strip()
        return text

    def process_invoice(self, content: bytes) -> Dict[str, Any]:
        try:
            logging.info("Processing invoice with Azure Document Intelligence...")
            poller = self.client.begin_analyze_document("prebuilt-invoice", document=content)
            result = poller.result()
            
            if not result.documents:
                logging.warning("No invoice data found in document")
                return None
                
            invoice = result.documents[0]
            extracted_data = {
                'vendor_info': self._extract_vendor_info(invoice),
                'invoice_info': self._extract_invoice_info(invoice),
                'amounts': self._extract_amounts(invoice),
                'line_items': self._extract_line_items(invoice),
                'confidence': invoice.confidence
            }
            
            self._log_extraction_results(extracted_data)
            return extracted_data
                
        except Exception as e:
            logging.error(f"Error processing document: {str(e)}")
            raise

    def _extract_vendor_info(self, invoice) -> Dict[str, Optional[str]]:
        vendor_info = {
            'name': None,
            'vat_number': None,
            'address': None,
            'country': 'Saudi Arabia'
        }
        
        try:
            fields = invoice.fields
            
            # Extract vendor name prioritizing Seller fields
            vendor_name = None
            vendor_fields = ['SellerName', 'VendorName', 'CompanyName']
            
            for field in vendor_fields:
                if field in fields and fields[field].value:
                    vendor_name = str(fields[field].value)
                    vendor_name = self.clean_text(vendor_name)
                    if vendor_name:
                        break
            
            vendor_info['name'] = vendor_name

            # Extract VAT number
            if 'VendorTaxId' in fields and fields['VendorTaxId'].value:
                vendor_info['vat_number'] = str(fields['VendorTaxId'].value).strip()
            
            # Extract address
            if 'VendorAddress' in fields and fields['VendorAddress'].value:
                vendor_info['address'] = self.clean_text(str(fields['VendorAddress'].value))
                
        except Exception as e:
            logging.error(f"Error extracting vendor info: {str(e)}")
            
        return vendor_info

    def _extract_invoice_info(self, invoice) -> Dict[str, Optional[str]]:
        invoice_info = {
            'number': None,
            'date': None,
            'due_date': None
        }
        
        try:
            fields = invoice.fields
            
            # Extract invoice number
            if 'InvoiceId' in fields:
                invoice_info['number'] = self.clean_text(str(fields['InvoiceId'].value))
            
            # Extract dates
            if 'InvoiceDate' in fields:
                date_val = fields['InvoiceDate'].value
                if isinstance(date_val, datetime):
                    invoice_info['date'] = date_val.strftime('%Y-%m-%d')
                elif isinstance(date_val, str):
                    try:
                        # Handle d/m/y format
                        day, month, year = date_val.split('/')
                        parsed_date = datetime(int(year), int(month), int(day))
                        invoice_info['date'] = parsed_date.strftime('%Y-%m-%d')
                    except:
                        invoice_info['date'] = date_val
            
            # Extract due date
            if 'DueDate' in fields:
                due_val = fields['DueDate'].value
                if isinstance(due_val, datetime):
                    invoice_info['due_date'] = due_val.strftime('%Y-%m-%d')
                elif isinstance(due_val, str):
                    try:
                        day, month, year = due_val.split('/')
                        parsed_date = datetime(int(year), int(month), int(day))
                        invoice_info['due_date'] = parsed_date.strftime('%Y-%m-%d')
                    except:
                        invoice_info['due_date'] = due_val
                    
        except Exception as e:
            logging.error(f"Error extracting invoice info: {str(e)}")
            
        return invoice_info

    def _extract_amounts(self, invoice) -> Dict[str, float]:
        amounts = {
            'subtotal': 0.0,
            'tax': 0.0,
            'total': 0.0
        }
        
        try:
            fields = invoice.fields
            
            # Helper function to extract amount
            def get_amount(field_value) -> float:
                if hasattr(field_value, 'amount'):
                    return float(field_value.amount)
                if isinstance(field_value, (int, float)):
                    return float(field_value)
                if isinstance(field_value, str):
                    # Remove currency symbols and convert
                    amount_str = field_value.replace('SAR', '').replace('$', '').replace(',', '').strip()
                    return float(amount_str)
                return 0.0
            
            # Extract amounts
            if 'SubTotal' in fields:
                amounts['subtotal'] = get_amount(fields['SubTotal'].value)
                
            if 'TotalTax' in fields:
                amounts['tax'] = get_amount(fields['TotalTax'].value)
            
            if 'InvoiceTotal' in fields:
                amounts['total'] = get_amount(fields['InvoiceTotal'].value)
            
            # Calculate missing values
            if amounts['total'] == 0 and amounts['subtotal'] > 0:
                if amounts['tax'] == 0:
                    amounts['tax'] = round(amounts['subtotal'] * 0.15, 2)  # 15% VAT
                amounts['total'] = amounts['subtotal'] + amounts['tax']
                
            # If only total is available
            elif amounts['total'] > 0 and amounts['subtotal'] == 0:
                amounts['subtotal'] = round(amounts['total'] / 1.15, 2)  # Remove 15% VAT
                amounts['tax'] = amounts['total'] - amounts['subtotal']
                
        except Exception as e:
            logging.error(f"Error extracting amounts: {str(e)}")
            
        return amounts

    def _extract_line_items(self, invoice) -> List[Dict[str, Any]]:
        line_items = []
        
        try:
            if 'Items' not in invoice.fields:
                return line_items

            items = invoice.fields.get('Items', {}).value or []
            
            for item in items:
                try:
                    line_item = {
                        'description': self.clean_text(str(item.value.get('Description', {}).value or 'Invoice Item')),
                        'quantity': float(item.value.get('Quantity', {}).value or 1),
                        'unit_price': float(item.value.get('UnitPrice', {}).value or 0),
                        'amount': float(item.value.get('Amount', {}).value or 0)
                    }
                    line_items.append(line_item)
                except Exception as e:
                    logging.error(f"Error processing line item: {str(e)}")
                    continue
                    
        except Exception as e:
            logging.error(f"Error extracting line items: {str(e)}")
            
        return line_items

    def _log_extraction_results(self, data: Dict[str, Any]):
        """Log extraction results for debugging"""
        logging.info("\nExtraction Results:")
        
        vendor_name = data['vendor_info'].get('name', 'Not found')
        invoice_number = data['invoice_info'].get('number', 'Not found')
        total_amount = data['amounts'].get('total', 0)
        
        logging.info(f"Vendor: {vendor_name}")
        logging.info(f"Invoice #: {invoice_number}")
        logging.info(f"Total: {total_amount:.2f} SAR")