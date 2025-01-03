from integration.xero.xero_client import XeroClient

def test_xero_auth():
    print("\nTesting Xero Authentication")
    print("=" * 50)
    
    client = XeroClient()
    
    print("\nConfiguration:")
    print(f"Client ID: {client.client_id[:8]}...")
    print(f"Tenant ID: {client.tenant_id}")
    
    # Test authentication
    print("\nAttempting authentication...")
    if client.authenticate():
        print("✓ Authentication successful!")
        
        # Try to get some data to verify access
        print("\nTesting API access...")
        contacts = client.get_contacts()
        if contacts:
            print(f"✓ Successfully retrieved {len(contacts)} contacts")
            for contact in contacts[:3]:  # Show first 3 contacts
                print(f"- {contact.get('Name', 'Unknown')}")
        else:
            print("No contacts found")
            
    else:
        print("❌ Authentication failed")

if __name__ == "__main__":
    test_xero_auth()