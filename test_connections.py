from services.email_monitor import EmailMonitor
from integration.xero.xero_client import XeroClient
from utils.logger import app_logger
import time

def test_xero_connection():
    """Test Xero API connection"""
    print("\nTesting Xero Connection...")
    print("=" * 50)
    
    try:
        client = XeroClient()
        client.authenticate()
        print("✓ Successfully connected to Xero")
        print(f"✓ Tenant ID: {client.tenant_id}")
        return True
    except Exception as e:
        print(f"❌ Xero connection failed: {str(e)}")
        return False

def test_email_connection():
    """Test Email connection"""
    print("\nTesting Email Connection...")
    print("=" * 50)
    
    try:
        with EmailMonitor() as monitor:
            print("✓ Successfully connected to email service")
            print("Testing email inbox access...")
            emails = monitor.check_new_emails()
            print(f"✓ Successfully checked inbox ({len(emails)} new emails found)")
            return True
    except Exception as e:
        print(f"❌ Email connection failed: {str(e)}")
        return False

def test_full_pipeline():
    """Test the complete pipeline"""
    print("\nTesting Complete Pipeline...")
    print("=" * 50)
    print("This test will:")
    print("1. Connect to email")
    print("2. Check for new emails")
    print("3. Connect to Xero")
    print("4. Process any found attachments")
    
    try:
        # Initialize connections
        xero_client = XeroClient()
        xero_client.authenticate()
        print("✓ Xero connection established")
        
        with EmailMonitor() as monitor:
            print("✓ Email connection established")
            
            # Check for new emails
            print("\nChecking for new emails...")
            emails = monitor.check_new_emails()
            
            if emails:
                print(f"\nFound {len(emails)} new emails:")
                for email in emails:
                    print(f"\nProcessing email:")
                    print(f"  Subject: {email['subject']}")
                    print(f"  From: {email['sender']}")
                    print(f"  Attachments: {len(email['attachments'])}")
            else:
                print("No new emails found")
                
        return True
    except Exception as e:
        print(f"❌ Pipeline test failed: {str(e)}")
        return False

def main():
    print("Starting Connection Tests")
    print("=" * 50)
    
    # Test individual components
    email_ok = test_email_connection()
    xero_ok = test_xero_connection()
    
    if email_ok and xero_ok:
        print("\nBase connections successful! Would you like to test the complete pipeline?")
        response = input("Test complete pipeline? (y/n): ").lower()
        
        if response == 'y':
            test_full_pipeline()
    else:
        print("\nConnection tests failed. Please fix the errors above before proceeding.")

if __name__ == "__main__":
    main()