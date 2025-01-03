import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fetch_contacts():
    # Load tokens
    with open("tokens.json", "r") as f:
        tokens = json.load(f)

    # API endpoint and headers
    url = "https://api.xero.com/api.xro/2.0/Contacts"
    headers = {
        "Authorization": f"Bearer {tokens['access_token']}",
        "Xero-tenant-id": os.getenv("XERO_TENANT_ID"),
        "Content-Type": "application/json"
    }

    # Make request
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("Contacts fetched successfully!")
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

    else:
        print(f"Failed to fetch contacts: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    fetch_contacts()
