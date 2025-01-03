from services.ms365_auth import MS365Auth
import time

def test_ms365():
    print("\nTesting Microsoft 365 Connection")
    print("=" * 50)
    print("\nConfiguration:")
    print(f"Redirect URI: http://localhost:8000/callback")
    
    try:
        # Initialize authentication
        auth = MS365Auth()
        print("\n1. Starting authentication process...")
        print("   (This will open your browser for consent)")
        
        if auth.authenticate():
            print("✓ Authentication successful")
            
            # Get mailbox
            print("\n2. Accessing mailbox...")
            mailbox = auth.get_mailbox()
            print("✓ Mailbox access successful")
            
            # Check for messages
            print("\n3. Checking for messages...")
            messages = auth.get_messages(limit=5)
            
            count = 0
            for message in messages:
                count += 1
                print(f"\nMessage {count}:")
                print(f"Subject: {message.subject}")
                print(f"From: {message.sender.address}")
                
            if count == 0:
                print("No messages found in inbox")
            
            print("\n✓ Test completed successfully!")
            return True
            
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Verify the redirect URI in Azure matches exactly: http://localhost:8000/callback")
        print("2. Ensure you've granted admin consent in Azure portal")
        print("3. Check if you need to wait a few minutes for Azure changes to propagate")
        return False

if __name__ == "__main__":
    test_ms365()