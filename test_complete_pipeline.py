from services.ms365_auth import MS365Auth
from processors.azure_extractor import AzureExtractor
from integration.xero.xero_client import XeroClient
import os
from datetime import datetime

class EnhancedPipeline:
    def __init__(self):
        self.email_client = MS365Auth()
        self.azure_extractor = AzureExtractor()
        self.xero_client = XeroClient()
        
        # Initialize Xero
        print("Initializing Xero connection...")
        self.xero_client.authenticate()

    def process_attachment(self, filepath: str) -> dict:
        """Process a single attachment with Azure Form Recognizer"""
        try:
            print(f"\nProcessing: {os.path.basename(filepath)}")
            print("-" * 50)
            
            # Read the file
            with open(filepath, 'rb') as f:
                file_content = f.read()
            
            # Process with Azure Form Recognizer
            print("Processing with Azure Form Recognizer...")
            extracted_data = self.azure_extractor.process_document(file_content)
            
            if not extracted_data:
                print("No invoice data found in document")
                return None
            
            # Print extracted data
            print("\nExtracted Invoice Data:")
            print(f"Vendor: {extracted_data['vendor_info']['name']}")
            print(f"Invoice Number: {extracted_data['invoice_info']['number']}")
            print(f"Total Amount: ${extracted_data['amounts']['total']:.2f}")
            
            if extracted_data['line_items']:
                print("\nLine Items:")
                for item in extracted_data['line_items']:
                    print(f"- {item['description']}: {item['quantity']} x ${item['unit_price']:.2f} = ${item['amount']:.2f}")
            
            # Ask for confirmation
            print("\nWould you like to:")
            print("1. Create Xero entry with these details")
            print("2. Enter details manually")
            print("3. Skip this attachment")
            
            choice = input("\nEnter choice (1-3): ").strip()
            
            if choice == '1':
                # Create invoice data for Xero
                invoice_data = {
                    'vendor_name': extracted_data['vendor_info']['name'],
                    'invoice_number': extracted_data['invoice_info']['number'],
                    'date': extracted_data['invoice_info']['date'],
                    'due_date': extracted_data['invoice_info']['due_date'],
                    'total_amount': extracted_data['amounts']['total'],
                    'line_items': extracted_data['line_items']
                }
                
                # Create Xero entry
                print("\nCreating Xero entry...")
                xero_response = self.xero_client.create_invoice_from_data(invoice_data)
                
                if xero_response:
                    print("\n✓ Invoice created successfully in Xero")
                    print(f"✓ Vendor: {xero_response['Contact']['Name']}")
                    print(f"✓ Amount: ${xero_response['Total']}")
                    print(f"✓ Invoice Number: {xero_response['InvoiceNumber']}")
                    return True
                    
            elif choice == '2':
                # Manual entry
                print("\nEnter invoice details manually:")
                vendor_name = input("Vendor name: ").strip()
                invoice_number = input("Invoice number: ").strip()
                amount = float(input("Amount: ").strip())
                date = input("Date (YYYY-MM-DD): ").strip()
                
                invoice_data = {
                    'vendor_name': vendor_name,
                    'invoice_number': invoice_number,
                    'date': date,
                    'total_amount': amount
                }
                
                xero_response = self.xero_client.create_invoice_from_data(invoice_data)
                if xero_response:
                    print("\n✓ Invoice created successfully in Xero")
                    print(f"✓ Vendor: {xero_response['Contact']['Name']}")
                    print(f"✓ Amount: ${xero_response['Total']}")
                    print(f"✓ Invoice Number: {xero_response['InvoiceNumber']}")
                    return True
            
            return extracted_data
            
        except Exception as e:
            print(f"\n❌ Error processing attachment: {str(e)}")
            return None

    def process_new_emails(self):
        """Process new emails with attachments"""
        try:
            print("\n1. Authenticating with Microsoft 365...")
            if not self.email_client.authenticate():
                raise Exception("Failed to authenticate with Microsoft 365")
                
            print("\n2. Checking for new emails with attachments...")
            messages = self.email_client.get_messages_with_attachments(limit=5)
            
            if not messages:
                print("No new emails with attachments found")
                return
                
            print(f"\nFound {len(messages)} new emails with attachments")
            
            for msg in messages:
                print(f"\nProcessing email: {msg['subject']}")
                attachments = self.email_client.get_message_attachments(msg['id'])
                
                for attachment in attachments:
                    name = attachment['name']
                    if name.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg')):
                        # Download attachment
                        filepath = self.email_client.download_attachment(msg['id'], attachment)
                        
                        if filepath:
                            # Process the attachment
                            processed = self.process_attachment(filepath)
                            
                            if processed:
                                mark_read = input("\nMark email as read? (y/n): ").lower()
                                if mark_read == 'y':
                                    self.email_client.mark_as_read(msg['id'])
                                    print("✓ Email marked as read")
                            
                            # Clean up temporary file
                            try:
                                os.remove(filepath)
                                print(f"✓ Cleaned up temporary file: {filepath}")
                            except:
                                pass
                    else:
                        print(f"Skipping non-document attachment: {name}")
            
            print("\n✓ Processing completed!")
            
        except Exception as e:
            print(f"\n❌ Error in pipeline: {str(e)}")

if __name__ == "__main__":
    pipeline = EnhancedPipeline()
    pipeline.process_new_emails()