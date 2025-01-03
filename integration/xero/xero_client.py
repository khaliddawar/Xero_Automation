import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN_FILE = "tokens.json"
SCOPES = "accounting.contacts accounting.transactions offline_access"

class XeroClient:
    def __init__(self):
        self.client_id = os.getenv("XERO_CLIENT_ID")
        self.client_secret = os.getenv("XERO_CLIENT_SECRET")
        self.redirect_uri = os.getenv("REDIRECT_URI")
        self.base_url = "https://api.xero.com"
        self.token_url = "https://identity.xero.com/connect/token"
        self.access_token = None
        self.refresh_token = None
        self.headers = {"Content-Type": "application/json"}
        self.load_tokens()

    def save_tokens(self, tokens):
        with open(TOKEN_FILE, "w") as f:
            json.dump(tokens, f)

    def load_tokens(self):
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r") as f:
                tokens = json.load(f)
                self.access_token = tokens.get("access_token")
                self.refresh_token = tokens.get("refresh_token")
                self.headers["Authorization"] = f"Bearer {self.access_token}"

    def is_token_expired(self):
        # Implement token expiry logic if needed
        return False  # Placeholder for token expiry check

    def ensure_token_valid(self):
        if self.access_token and not self.is_token_expired():
            return True
        return self.refresh_tokens()

    def refresh_tokens(self):
        if not self.refresh_token:
            print("No refresh token available. Please authenticate.")
            return False
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        response = requests.post(self.token_url, data=payload)
        if response.status_code == 200:
            tokens = response.json()
            self.save_tokens(tokens)
            self.access_token = tokens["access_token"]
            self.headers["Authorization"] = f"Bearer {self.access_token}"
            return True
        else:
            print(f"Failed to refresh token: {response.text}")
            return False

    def start_auth_flow(self):
        auth_url = (
            f"https://login.xero.com/identity/connect/authorize?"
            f"response_type=code&client_id={self.client_id}&redirect_uri={self.redirect_uri}&"
            f"scope={SCOPES}&state=12345"
        )
        print(f"Visit this URL to authorize:\n{auth_url}")
