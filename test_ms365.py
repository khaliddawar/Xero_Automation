from services.email_monitor import EmailMonitor
from utils.logger import app_logger

def test_ms365_connection():
    print("\nTesting Microsoft 365 Connection")
    print("=" * 50)
    
    try:
        with EmailMonitor() as monitor:
            print("\n1. Testing authentication...")
            # This will open a browser window for authentication
            
            print("\n2. Checking for new emails...")
            emails = monitor.check_new_emails()
            
            if emails:
                print(f"\nFound {len(emails)} new emails:")
                for email in emails:
                    print(f"\nSubject: {email['subject']}")
                    print(f"From: {email['sender']}")
                    print(f"Attachments: {len(email['attachments'])}")
            else:
                print("\nNo new emails found")
                
            print("\n✓ Test completed successfully!")
            return True
            
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_ms365_connection()