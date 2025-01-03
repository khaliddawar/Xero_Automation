import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def refresh_tokens():
    # Load environment variables
    client_id = os.getenv("XERO_CLIENT_ID")
    client_secret = os.getenv("XERO_CLIENT_SECRET")

    # Load current tokens
    with open("tokens.json", "r") as f:
        tokens = json.load(f)

    # Token refresh request
    url = "https://identity.xero.com/connect/token"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": tokens["refresh_token"],
        "client_id": client_id,
        "client_secret": client_secret,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    # Make request
    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        new_tokens = response.json()
        with open("tokens.json", "w") as f:
            json.dump(new_tokens, f)
        print("Tokens refreshed successfully!")
    else:
        print(f"Failed to refresh tokens: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    refresh_tokens()
