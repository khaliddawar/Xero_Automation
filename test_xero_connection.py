from integration.xero.xero_client import XeroClient
from utils.config import config
import json

def test_xero_connection():
    try:
        print("\nStarting Xero connection test...")
        print("-" * 50)
        
        # Check config values
        print("\nChecking configuration...")
        if not config.XERO_CLIENT_ID or not config.XERO_CLIENT_SECRET:
            raise Exception("Missing Xero credentials in .env file")
        print("✓ Configuration found")
        
        # Initialize client
        print("\nInitializing Xero client...")
        client = XeroClient()
        print("✓ Client initialized")
        
        # Authenticate
        print("\nStarting authentication process...")
        client.authenticate()
        print("✓ Authentication successful")
        
        # Test access by getting organisations
        print("\nFetching organisation details...")
        organisations = client.get_organisations()
        
        if organisations:
            print("\nOrganizations found:")
            print("-" * 30)
            for org in organisations:
                print(f"Name: {org.get('Name', 'Unknown')}")
                print(f"ID: {org.get('OrganisationID', 'Unknown')}")
                print(f"Status: {org.get('OrganisationStatus', 'Unknown')}")
                print("-" * 30)
        else:
            print("No organisations found.")
        
        print("\n✓ Xero connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Xero connection test failed: {str(e)}")
        print("\nPlease verify:")
        print("1. Your Xero credentials are correct in .env file")
        print("2. Your Xero app has the required permissions")
        print("3. You have an active Xero subscription")
        return False

if __name__ == "__main__":
    test_xero_connection()