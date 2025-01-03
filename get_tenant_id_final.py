import requests
import base64
import webbrowser
from urllib.parse import urlencode, parse_qs
import json

def get_xero_tenant_id():
    # Your actual credentials
    CLIENT_ID = 'BCB7EE00E1894B1ABBC52AA949CC4A9A'
    CLIENT_SECRET = '_Wr4PWGZ0DgykaTj_A4-ws7H9SZ3YzJk-yBm4lNk51RZiBF4'
    REDIRECT_URI = 'http://localhost:8000'
    
    # Step 1: Build authorization URL
    auth_url = 'https://login.xero.com/identity/connect/authorize'
    auth_params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'offline_access openid profile email accounting.transactions accounting.settings accounting.contacts',
        'state': '123'
    }
    
    full_auth_url = f"{auth_url}?{urlencode(auth_params)}"
    
    print("\n1. Opening browser for authorization...")
    webbrowser.open(full_auth_url)
    
    print("\n2. After authorizing, copy the ENTIRE URL you were redirected to:")
    callback_url = input().strip()
    
    try:
        # Extract code from callback URL
        params = parse_qs(callback_url.split('?')[1])
        code = params['code'][0]
        print(f"\nReceived authorization code: {code[:15]}...")
        
        # Exchange code for tokens
        token_url = 'https://identity.xero.com/connect/token'
        
        # Create basic auth header
        auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
        basic_auth = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {basic_auth}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI
        }
        
        print("\n3. Exchanging code for tokens...")
        token_response = requests.post(token_url, headers=headers, data=data)
        
        if token_response.status_code != 200:
            print(f"\nError getting tokens. Status code: {token_response.status_code}")
            print("Response:", token_response.text)
            return None
            
        tokens = token_response.json()
        access_token = tokens.get('access_token')
        
        if not access_token:
            print("\nNo access token received!")
            print("Response:", tokens)
            return None
            
        print("✓ Access token received successfully!")
        
        # Get Connections/Tenant ID
        print("\n4. Getting tenant information...")
        connections_url = 'https://api.xero.com/connections'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        connections_response = requests.get(connections_url, headers=headers)
        
        if connections_response.status_code != 200:
            print(f"\nError getting connections. Status code: {connections_response.status_code}")
            print("Response:", connections_response.text)
            return None
            
        connections = connections_response.json()
        
        if not connections:
            print("\nNo connections found!")
            return None
            
        tenant_id = connections[0].get('tenantId')
        tenant_name = connections[0].get('tenantName')
        
        print("\nConnection found:")
        print(f"✓ Tenant ID: {tenant_id}")
        print(f"✓ Tenant Name: {tenant_name}")
        
        # Save to .env file
        env_content = ""
        try:
            with open('.env', 'r') as f:
                env_content = f.read()
        except FileNotFoundError:
            pass

        env_updated = False
        new_env_content = []
        
        # Update existing XERO_TENANT_ID if present
        if env_content:
            for line in env_content.splitlines():
                if line.startswith('XERO_TENANT_ID='):
                    new_env_content.append(f'XERO_TENANT_ID={tenant_id}')
                    env_updated = True
                else:
                    new_env_content.append(line)
        
        # Add XERO_TENANT_ID if not present
        if not env_updated:
            new_env_content.append(f'XERO_TENANT_ID={tenant_id}')
        
        # Write back to .env file
        with open('.env', 'w') as f:
            f.write('\n'.join(new_env_content))
        
        print("\n✓ Tenant ID has been saved to .env file!")
        return tenant_id
        
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    print("Starting Xero tenant ID retrieval process...")
    tenant_id = get_xero_tenant_id()
    
    if tenant_id:
        print("\n✓ Process completed successfully!")
    else:
        print("\n❌ Failed to retrieve tenant ID. Please check the errors above.")