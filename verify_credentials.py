import os
import requests
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)

def verify_credentials():
    load_dotenv()
    
    client_id = os.getenv("XERO_CLIENT_ID")
    client_secret = os.getenv("XERO_CLIENT_SECRET")
    
    print("\nChecking Xero credentials...")
    print(f"Client ID: {client_id[:5]}...{client_id[-5:] if client_id else 'Not found'}")
    print(f"Client Secret: {client_secret[:5]}...{client_secret[-5:] if client_secret else 'Not found'}")
    
    # Try authentication
    auth = (client_id, client_secret)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "scope": "accounting.transactions"
    }
    
    try:
        response = requests.post(
            "https://identity.xero.com/connect/token",
            auth=auth,
            headers=headers,
            data=data
        )
        
        print("\nAuth Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}\n")
        
        if response.status_code == 200:
            print("✅ Credentials are valid!")
            token = response.json()["access_token"]
            
            # Try to use the token
            api_headers = {
                "Authorization": f"Bearer {token}",
                "xero-tenant-id": os.getenv("XERO_TENANT_ID"),
                "Content-Type": "application/json"
            }
            
            api_response = requests.get(
                "https://api.xero.com/api.xro/2.0/Organisation",
                headers=api_headers
            )
            
            print("\nAPI Test:")
            print(f"Status Code: {api_response.status_code}")
            print(f"Response: {api_response.text}\n")
            
        else:
            print("❌ Authentication failed!")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    verify_credentials()