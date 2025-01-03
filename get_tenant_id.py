import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_tenant_id():
    """Get the tenant ID from Xero"""
    client_id = os.getenv("XERO_CLIENT_ID")
    client_secret = os.getenv("XERO_CLIENT_SECRET")

    # Get access token
    token_url = "https://identity.xero.com/connect/token"
    auth_headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    auth_data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "accounting.transactions accounting.contacts.read accounting.contacts.write offline_access"
    }
    
    print("Getting access token...")
    token_response = requests.post(token_url, headers=auth_headers, data=auth_data)
    
    if token_response.status_code != 200:
        print(f"Failed to get token: {token_response.text}")
        return
        
    access_token = token_response.json()["access_token"]
    
    # Get connections/tenants
    connections_url = "https://api.xero.com/connections"
    connections_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print("Getting tenant information...")
    connections_response = requests.get(connections_url, headers=connections_headers)
    
    if connections_response.status_code != 200:
        print(f"Failed to get connections: {connections_response.text}")
        return
        
    tenants = connections_response.json()
    
    if not tenants:
        print("No tenants found!")
        return
        
    print("\nAvailable Tenants:")
    for tenant in tenants:
        print(f"\nTenant ID: {tenant['tenantId']}")
        print(f"Tenant Name: {tenant.get('tenantName', 'N/A')}")
        print(f"Tenant Type: {tenant.get('tenantType', 'N/A')}")
        
    return tenants[0]['tenantId']  # Return first tenant ID

if __name__ == "__main__":
    tenant_id = get_tenant_id()
    if tenant_id:
        print(f"\nAdd this tenant ID to your .env file:")
        print(f"XERO_TENANT_ID={tenant_id}")
