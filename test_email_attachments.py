from services.ms365_auth import MS365Auth
from datetime import datetime

def test_attachments():
    print("\nTesting Email Attachment Processing")
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
            
            # Get messages with attachments
            print("\n2. Checking for unread messages with attachments...")
            messages = auth.get_messages_with_attachments(limit=5)
            
            if messages:
                print(f"\nFound {len(messages)} unread messages with attachments:")
                
                for msg in messages:
                    print(f"\nEmail Details:")
                    print(f"Subject: {msg['subject']}")
                    print(f"From: {msg['from']['emailAddress']['address']}")
                    print(f"Received: {msg['receivedDateTime']}")
                    
                    # Get attachments for this message
                    attachments = auth.get_message_attachments(msg['id'])
                    
                    if attachments:
                        print(f"Attachments ({len(attachments)}):")
                        for attachment in attachments:
                            print(f"- {attachment['name']} ({attachment.get('contentType', 'unknown type')})")
                            
                            # Option to download attachment
                            download = input("\nDownload this attachment? (y/n): ").lower()
                            if download == 'y':
                                filepath = auth.download_attachment(msg['id'], attachment)
                                if filepath:
                                    print(f"✓ Downloaded to: {filepath}")
                                else:
                                    print("❌ Failed to download attachment")
                        
                        # Option to mark as read
                        mark_read = input("\nMark this email as read? (y/n): ").lower()
                        if mark_read == 'y':
                            if auth.mark_as_read(msg['id']):
                                print("✓ Marked as read")
                            else:
                                print("❌ Failed to mark as read")
            else:
                print("No unread messages with attachments found")
                
            print("\n✓ Test completed successfully!")
            return True
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_attachments()