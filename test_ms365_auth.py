from services.ms365_auth import MS365Auth
import json
from datetime import datetime

def test_ms365():
    print("\nTesting Microsoft 365 Connection")
    print("=" * 50)
    
    try:
        # Initialize auth
        auth = MS365Auth()
        print("\nConfiguration:")
        print(f"Client ID: {auth.client_id[:8]}...")
        print(f"Tenant ID: {auth.tenant_id}")
        
        # Test authentication
        print("\n1. Testing authentication...")
        if auth.authenticate():
            print("✓ Authentication successful!")
            
            # Test getting messages
            print("\n2. Retrieving recent messages...")
            messages = auth.get_messages(limit=5)
            
            if messages:
                print(f"\nFound {len(messages)} messages:")
                for msg in messages:
                    subject = msg.get('subject', 'No subject')
                    sender = msg.get('from', {}).get('emailAddress', {}).get('address', 'Unknown')
                    received = msg.get('receivedDateTime', '')
                    print(f"\nSubject: {subject}")
                    print(f"From: {sender}")
                    print(f"Received: {received}")
            else:
                print("No messages found")
                
            print("\n✓ Test completed successfully!")
            return True
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Verify Azure app registration:")
        print("   - Client ID is correct")
        print("   - Client Secret is correct (not expired)")
        print("   - API permissions include Mail.Read")
        print(f"2. Verify configuration:")
        print("   - MS365_CLIENT_ID is set correctly")
        print("   - MS365_CLIENT_SECRET is set correctly")
        print("   - MS365_TENANT_ID is set correctly")
        return False

if __name__ == "__main__":
    test_ms365()