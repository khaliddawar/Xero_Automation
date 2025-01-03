import json
import requests
from datetime import datetime

# Load tokens from the tokens.json file
def load_tokens():
    try:
        with open('tokens.json', 'r') as file:
            data = json.load(file)
        
        if 'access_token' not in data or 'tenant_id' not in data:
            print(f"Tokens in file: {data}")
            raise KeyError("Either 'access_token' or 'tenant_id' is missing in tokens.json")
        
        return data['access_token'], data['tenant_id']
    except FileNotFoundError:
        raise FileNotFoundError("The tokens.json file does not exist. Please authenticate first.")
    except json.JSONDecodeError:
        raise ValueError("The tokens.json file is not a valid JSON file.")

# Create an invoice
def create_invoice():
    try:
        # Load the access token and tenant ID
        access_token, tenant_id = load_tokens()

        # Endpoint for creating an invoice
        url = "https://api.xero.com/api.xro/2.0/Invoices"

        # Headers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "xero-tenant-id": tenant_id,
            "Content-Type": "application/json"
        }

        # Invoice payload
        payload = {
            "Type": "ACCREC",
            "Contact": {
                "ContactID": "9800277c-62cc-4367-b06e-68f1e0518f36"  # Replace with a valid ContactID
            },
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "DueDate": (datetime.now().strftime("%Y-%m-%d")),
            "LineItems": [
                {
                    "Description": "Consulting services",
                    "Quantity": 1.0,
                    "UnitAmount": 100.0,
                    "AccountCode": "200"  # Replace with a valid AccountCode
                }
            ],
            "Status": "DRAFT"
        }

        # Send POST request
        response = requests.post(url, headers=headers, json=payload)

        # Handle response
        if response.status_code == 200:
            print("Invoice created successfully!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Failed to create invoice. Status Code: {response.status_code}")
            print("Response Text:", response.text)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_invoice()
