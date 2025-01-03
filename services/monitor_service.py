import time
from datetime import datetime
from .email_monitor import EmailMonitor
from processors.ocr import OCRProcessor
from processors.text_analyzer import TextAnalyzer
from integration.xero.xero_client import XeroClient
from utils.logger import app_logger
import os

class MonitorService:
    def __init__(self):
        self.email_monitor = EmailMonitor()
        self.ocr_processor = OCRProcessor()
        self.text_analyzer = TextAnalyzer()
        self.xero_client = None  # Will initialize during processing

    def initialize_xero(self):
        """Initialize Xero client if not already initialized"""
        if not self.xero_client:
            self.xero_client = XeroClient()
            self.xero_client.authenticate()

    def process_attachments(self, attachments):
        """Process email attachments"""
        results = []
        for attachment in attachments:
            try:
                # Read attachment
                with open(attachment, 'rb') as f:
                    content = f.read()

                # Process based on file type
                file_ext = os.path.splitext(attachment)[1].lower()
                if file_ext == '.pdf':
                    ocr_results = self.ocr_processor.process_pdf(content)
                else:
                    ocr_results = self.ocr_processor.process_image(content)

                # Analyze extracted text
                analysis_results = self.text_analyzer.process_text(ocr_results['text'])
                
                results.append({
                    'filename': os.path.basename(attachment),
                    'ocr_results': ocr_results,
                    'analysis_results': analysis_results
                })

            except Exception as e:
                app_logger.error(f"Error processing attachment {attachment}: {str(e)}")

        return results

    def create_xero_invoice(self, analysis_results, email_data):
        """Create invoice in Xero based on analysis results"""
        try:
            # Ensure Xero is initialized
            self.initialize_xero()

            # Extract invoice data
            patterns = analysis_results.get('patterns', {})
            entities = analysis_results.get('entities', {})

            amount = None
            amounts = patterns.get('amount', [])
            if amounts:
                # Convert first amount string to float
                amount_str = amounts[0].replace('$', '').replace(',', '')
                try:
                    amount = float(amount_str)
                except ValueError:
                    app_logger.error(f"Could not convert amount: {amounts[0]}")
                    return None

            invoice_data = {
                "Type": "ACCPAY",
                "Contact": {
                    "Name": entities.get('ORG', ['Unknown Vendor'])[0]
                },
                "LineItems": [
                    {
                        "Description": f"Invoice from email: {email_data['subject']}",
                        "Quantity": 1.0,
                        "UnitAmount": amount if amount else 0.0,
                        "AccountCode": "200"  # Default expense account
                    }
                ],
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Reference": patterns.get('invoice_number', [''])[0],
                "Status": "DRAFT"
            }

            response = self.xero_client.create_invoice(invoice_data)
            return response

        except Exception as e:
            app_logger.error(f"Error creating Xero invoice: {str(e)}")
            return None

    def process_emails(self):
        """Process new emails"""
        try:
            # Use context manager for email connection
            with EmailMonitor() as email_monitor:
                app_logger.info("Checking for new emails...")
                new_emails = email_monitor.check_new_emails()
                
                if new_emails:
                    app_logger.info(f"Found {len(new_emails)} new emails")
                    
                    for email_data in new_emails:
                        app_logger.info(f"Processing email: {email_data['subject']}")
                        
                        # Process attachments
                        if email_data['attachments']:
                            attachment_results = self.process_attachments(email_data['attachments'])
                            
                            # Create invoices based on results
                            for result in attachment_results:
                                invoice = self.create_xero_invoice(
                                    result['analysis_results'],
                                    email_data
                                )
                                
                                if invoice:
                                    app_logger.info(f"Created invoice: {invoice.get('InvoiceID')}")
                                    
                            # Clean up temporary files
                            for attachment in email_data['attachments']:
                                try:
                                    os.remove(attachment)
                                except:
                                    pass
                else:
                    app_logger.info("No new emails found")

        except Exception as e:
            app_logger.error(f"Error in process_emails: {str(e)}")

    def run(self, interval=300):  # 5 minutes default interval
        """Run the monitoring service"""
        app_logger.info("Starting email monitoring service...")
        
        while True:
            try:
                self.process_emails()
                time.sleep(interval)
                
            except KeyboardInterrupt:
                app_logger.info("Stopping email monitoring service...")
                break
            except Exception as e:
                app_logger.error(f"Error in monitoring service: {str(e)}")
                time.sleep(interval)  # Wait before retrying
