import os
from processors.azure_doc_intelligence import AzureDocProcessor
from services.ms365_auth import MS365Auth
from integration.xero.xero_client import XeroClient
import logging
from datetime import datetime
import sys

# Set up logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_test.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

class SystemTester:
    def __init__(self):
        self.azure_processor = None
        self.email_client = None
        self.xero_client = None
        
        # Use simple symbols that work in all consoles
        self.SUCCESS_MARK = '[OK]'
        self.FAIL_MARK = '[FAIL]'

    def test_azure_credentials(self):
        """Test Azure Document Intelligence credentials and connection"""
        try:
            logging.info("Testing Azure Document Intelligence connection...")
            
            # Check environment variables
            endpoint = os.getenv("AZURE_DOC_INTELLIGENCE_ENDPOINT")
            key = os.getenv("AZURE_DOC_INTELLIGENCE_KEY")
            
            if not endpoint or not key:
                logging.error("Azure credentials not found in environment variables")
                return False
            
            # Initialize processor
            self.azure_processor = AzureDocProcessor()
            logging.info(f"{self.SUCCESS_MARK} Azure Document Intelligence credentials verified")
            return True
            
        except Exception as e:
            logging.error(f"Azure credential test failed: {str(e)}")
            return False

    def test_document_processing(self, test_file_path):
        """Test document processing with a sample file"""
        try:
            logging.info(f"Testing document processing with file: {test_file_path}")
            
            if not os.path.exists(test_file_path):
                logging.error(f"Test file not found: {test_file_path}")
                return False
            
            # Read test file
            with open(test_file_path, 'rb') as f:
                content = f.read()
            
            # Process with Azure
            result = self.azure_processor.process_invoice(content)
            
            if result:
                logging.info("Document processing results:")
                logging.info(f"Vendor: {result['vendor_info'].get('name', 'Not found')}")
                logging.info(f"Invoice Number: {result['invoice_info'].get('number', 'Not found')}")
                logging.info(f"Amount: ${result['amounts'].get('total', 0):.2f}")
                logging.info(f"Confidence: {result.get('confidence', 0)*100:.2f}%")
                return True
            else:
                logging.error("Document processing returned no results")
                return False
                
        except Exception as e:
            logging.error(f"Document processing test failed: {str(e)}")
            return False

    def test_ms365_connection(self):
        """Test Microsoft 365 connection"""
        try:
            logging.info("Testing Microsoft 365 connection...")
            
            self.email_client = MS365Auth()
            if self.email_client.authenticate():
                logging.info(f"{self.SUCCESS_MARK} Microsoft 365 connection successful")
                return True
            else:
                logging.error("Microsoft 365 authentication failed")
                return False
                
        except Exception as e:
            logging.error(f"Microsoft 365 test failed: {str(e)}")
            return False

    def test_xero_connection(self):
        """Test Xero API connection"""
        try:
            logging.info("Testing Xero connection...")
            
            self.xero_client = XeroClient()
            if self.xero_client.authenticate():
                logging.info(f"{self.SUCCESS_MARK} Xero connection successful")
                return True
            else:
                logging.error("Xero authentication failed")
                return False
                
        except Exception as e:
            logging.error(f"Xero test failed: {str(e)}")
            return False

    def test_end_to_end(self, test_file_path):
        """Test complete end-to-end process"""
        try:
            logging.info("Starting end-to-end test...")
            
            # Step 1: Process document
            with open(test_file_path, 'rb') as f:
                content = f.read()
            
            extracted_data = self.azure_processor.process_invoice(content)
            if not extracted_data:
                logging.error("Document extraction failed")
                return False
            
            # Step 2: Create Xero entry
            invoice_data = {
                'vendor_name': extracted_data['vendor_info'].get('name'),
                'invoice_number': extracted_data['invoice_info'].get('number'),
                'date': extracted_data['invoice_info'].get('date'),
                'due_date': extracted_data['invoice_info'].get('due_date'),
                'total_amount': extracted_data['amounts'].get('total'),
                'line_items': extracted_data.get('line_items', [])
            }
            
            xero_response = self.xero_client.create_invoice_from_data(invoice_data)
            
            if xero_response:
                logging.info("End-to-end test results:")
                logging.info(f"{self.SUCCESS_MARK} Document processed successfully")
                logging.info(f"{self.SUCCESS_MARK} Xero invoice created: {xero_response['InvoiceNumber']}")
                logging.info(f"Vendor: {xero_response['Contact']['Name']}")
                logging.info(f"Amount: ${xero_response['Total']}")
                return True
            else:
                logging.error("Failed to create Xero invoice")
                return False
                
        except Exception as e:
            logging.error(f"End-to-end test failed: {str(e)}")
            return False

    def run_all_tests(self, test_file_path):
        """Run all system tests"""
        logging.info("Starting system tests...")
        logging.info("=" * 50)
        
        # Test Azure setup
        azure_ok = self.test_azure_credentials()
        logging.info("-" * 50)
        
        # Test Microsoft 365
        ms365_ok = self.test_ms365_connection()
        logging.info("-" * 50)
        
        # Test Xero
        xero_ok = self.test_xero_connection()
        logging.info("-" * 50)
        
        # If all connections successful, test processing
        if azure_ok and ms365_ok and xero_ok:
            # Test document processing
            doc_ok = self.test_document_processing(test_file_path)
            logging.info("-" * 50)
            
            # Test end-to-end
            if doc_ok:
                e2e_ok = self.test_end_to_end(test_file_path)
                logging.info("-" * 50)
            else:
                e2e_ok = False
            
            # Summary
            logging.info("\nTest Summary:")
            logging.info(f"Azure Document Intelligence: {self.SUCCESS_MARK if azure_ok else self.FAIL_MARK}")
            logging.info(f"Microsoft 365 Connection: {self.SUCCESS_MARK if ms365_ok else self.FAIL_MARK}")
            logging.info(f"Xero Connection: {self.SUCCESS_MARK if xero_ok else self.FAIL_MARK}")
            logging.info(f"Document Processing: {self.SUCCESS_MARK if doc_ok else self.FAIL_MARK}")
            logging.info(f"End-to-End Test: {self.SUCCESS_MARK if e2e_ok else self.FAIL_MARK}")
            
            return all([azure_ok, ms365_ok, xero_ok, doc_ok, e2e_ok])
        else:
            logging.error("Basic connection tests failed, skipping further tests")
            return False

if __name__ == "__main__":
    # Create test directory if it doesn't exist
    test_dir = "test_samples"
    os.makedirs(test_dir, exist_ok=True)
    
    # Define test file path
    test_file = os.path.join(test_dir, "test_invoice.pdf")
    
    # Check if test file exists
    if not os.path.exists(test_file):
        logging.error(f"Please place a test invoice at: {test_file}")
        exit(1)
    
    # Run tests
    tester = SystemTester()
    success = tester.run_all_tests(test_file)
    
    if success:
        logging.info("\n[SUCCESS] All tests passed successfully!")
    else:
        logging.error("\n[FAILED] Some tests failed. Check logs for details.")