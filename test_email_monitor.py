from services.email_monitor import EmailMonitor
import time

def test_email_monitor():
    print("\nTesting Email Monitoring")
    print("=" * 50)
    
    try:
        with EmailMonitor() as monitor:
            print("\n✓ Successfully initialized email monitor")
            
            # Monitor for a short period
            duration = 60  # 1 minute
            print(f"\nMonitoring inbox for {duration} seconds...")
            print("You can send a test email now to: {monitor.email_user}")
            
            end_time = time.time() + duration
            while time.time() < end_time:
                # Check for new emails
                new_emails = monitor.check_new_emails()
                
                if new_emails:
                    print("\nFound new emails!")
                    for email in new_emails:
                        print(f"\nEmail Details:")
                        print(f"  Subject: {email['subject']}")
                        print(f"  From: {email['sender']}")
                        print(f"  Attachments: {len(email['attachments'])}")
                        if email['attachments']:
                            print("  Attachment files:")
                            for attachment in email['attachments']:
                                print(f"    - {attachment}")
                
                # Wait a bit before next check
                remaining = int(end_time - time.time())
                print(f"\rTime remaining: {remaining} seconds...  ", end="", flush=True)
                time.sleep(5)  # Check every 5 seconds
            
            print("\n\nMonitoring complete!")
            return True
            
    except Exception as e:
        print(f"\n❌ Error during monitoring: {str(e)}")
        return False

if __name__ == "__main__":
    test_email_monitor()