import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fetch_invoices():
    # Load tokens
    with open("tokens.json", "r") as f:
        tokens = json.load(f)

    # API endpoint and headers
    url = "https://api.xero.com/api.xro/2.0/Invoices"
    headers = {
        "Authorization": f"Bearer {tokens['access_token']}",
        "Xero-tenant-id": os.getenv("XERO_TENANT_ID"),
        "Accept": "application/json",  # Ensure JSON response
        "Content-Type": "application/json"
    }

    # Make the request
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        try:
            data = response.json()
            print("Invoices fetched successfully!")
            print(json.dumps(data, indent=2))

            # Save to a file
            with open("invoices.json", "w") as f:
                json.dump(data, f, indent=2)
        except json.JSONDecodeError:
            print("Failed to parse JSON response.")
    else:
        print("Error fetching invoices.")
        print(f"Response Text: {response.text}")

if __name__ == "__main__":
    fetch_invoices()
