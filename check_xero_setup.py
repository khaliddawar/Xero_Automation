import os
import requests
import json
import webbrowser
from urllib.parse import quote
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

# Store tokens temporarily (in production, use proper storage)
tokens = {}

@app.get("/")
async def root():
    """Root endpoint to initiate OAuth flow"""
    client_id = os.getenv("XERO_CLIENT_ID")
    redirect_uri = "http://localhost:8000/oauth-callback"
    scopes = "openid profile email accounting.transactions accounting.contacts offline_access"
    
    auth_url = (
        f"https://login.xero.com/identity/connect/authorize?"
        f"response_type=code&"
        f"client_id={client_id}&"
        f"redirect_uri={quote(redirect_uri)}&"
        f"scope={quote(scopes)}"
    )
    
    return HTMLResponse(f"""
        <html>
            <body>
                <h1>Xero OAuth Setup</h1>
                <p>Click the button below to start OAuth flow:</p>
                <a href="{auth_url}"><button>Connect to Xero</button></a>
            </body>
        </html>
    """)

@app.get("/oauth-callback")
async def oauth_callback(code: str = None, error: str = None):
    """Handle OAuth callback"""
    if error:
        return HTMLResponse(f"Error: {error}")
        
    if not code:
        return HTMLResponse("No code received")
        
    # Exchange code for tokens
    token_url = "https://identity.xero.com/connect/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost:8000/oauth-callback",
        "client_id": os.getenv("XERO_CLIENT_ID"),
        "client_secret": os.getenv("XERO_CLIENT_SECRET")
    }
    
    try:
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            tokens.update(response.json())
            
            # Get tenant information
            connections_url = "https://api.xero.com/connections"
            headers = {
                "Authorization": f"Bearer {tokens['access_token']}",
                "Content-Type": "application/json"
            }
            
            connections_response = requests.get(connections_url, headers=headers)
            if connections_response.status_code == 200:
                tenants = connections_response.json()
                tenant_info = "<br>".join([
                    f"Tenant ID: {tenant['tenantId']}<br>"
                    f"Tenant Name: {tenant.get('tenantName', 'N/A')}<br><br>"
                    for tenant in tenants
                ])
                
                # Test API access
                if tenants:
                    test_tenant_id = tenants[0]['tenantId']
                    api_url = "https://api.xero.com/api.xro/2.0/Organisation"
                    api_headers = {
                        "Authorization": f"Bearer {tokens['access_token']}",
                        "xero-tenant-id": test_tenant_id,
                        "Content-Type": "application/json"
                    }
                    
                    api_response = requests.get(api_url, headers=api_headers)
                    api_status = "Success" if api_response.status_code == 200 else f"Failed: {api_response.text}"
                else:
                    api_status = "No tenants available to test"
                
                # Save the first tenant ID to .env
                if tenants:
                    env_path = os.path.join(os.path.dirname(__file__), '.env')
                    with open(env_path, 'r') as file:
                        env_lines = file.readlines()
                    
                    tenant_id_line = f"XERO_TENANT_ID={tenants[0]['tenantId']}\n"
                    tenant_id_found = False
                    
                    for i, line in enumerate(env_lines):
                        if line.startswith('XERO_TENANT_ID='):
                            env_lines[i] = tenant_id_line
                            tenant_id_found = True
                            break
                    
                    if not tenant_id_found:
                        env_lines.append(tenant_id_line)
                    
                    with open(env_path, 'w') as file:
                        file.writelines(env_lines)
                
                return HTMLResponse(f"""
                    <html>
                        <body>
                            <h1>Xero Setup Complete!</h1>
                            <h2>Authentication Status:</h2>
                            <p>✅ Successfully authenticated</p>
                            
                            <h2>Available Tenants:</h2>
                            <p>{tenant_info}</p>
                            
                            <h2>API Test Status:</h2>
                            <p>{api_status}</p>
                            
                            <h2>Next Steps:</h2>
                            <p>1. The first tenant ID has been saved to your .env file</p>
                            <p>2. You can now close this window and use the Xero API</p>
                        </body>
                    </html>
                """)
            else:
                return HTMLResponse(f"Failed to get tenant information: {connections_response.text}")
                
        else:
            return HTMLResponse(f"Failed to exchange code for tokens: {response.text}")
            
    except Exception as e:
        logger.error(f"Error in oauth_callback: {str(e)}")
        return HTMLResponse(f"Error during token exchange: {str(e)}")

def run_setup():
    """Run the OAuth setup server"""
    print("\n=== Starting Xero OAuth Setup ===\n")
    print("1. Opening browser to start OAuth flow...")
    webbrowser.open("http://localhost:8000")
    print("\n2. Complete the authentication in your browser")
    print("\n3. The application will automatically update your .env file with the tenant ID")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    run_setup()