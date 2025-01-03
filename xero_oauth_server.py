from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the request URL
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        # Handle OAuth callback
        if "code" in query_params:
            auth_code = query_params["code"][0]
            print(f"Authorization code received: {auth_code}")
            self.exchange_code_for_tokens(auth_code)
        else:
            print("Authorization code not found in request.")

        # Send response to the browser
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Authorization complete. You can close this tab.")

    def exchange_code_for_tokens(self, auth_code):
        token_url = "https://identity.xero.com/connect/token"

        # Prepare payload and headers
        payload = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": os.getenv("REDIRECT_URI"),
            "client_id": os.getenv("XERO_CLIENT_ID"),
            "client_secret": os.getenv("XERO_CLIENT_SECRET"),
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # Make the token request
        response = requests.post(token_url, data=payload, headers=headers)

        if response.status_code == 200:
            tokens = response.json()
            # Save tokens to a file
            with open("tokens.json", "w") as f:
                json.dump(tokens, f)
            print("Tokens saved successfully.")
        else:
            print(f"Failed to obtain tokens: {response.text}")

def run_server():
    # Start the HTTP server
    server_address = ("", 8000)
    httpd = HTTPServer(server_address, OAuthHandler)
    print("Starting OAuth server on port 8000...")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
