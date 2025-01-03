import requests
import json

def fetch_and_save_tenant_id():
    with open('tokens.json', 'r') as file:
        tokens = json.load(file)

    headers = {
        "Authorization": f"Bearer {tokens['access_token']}",
        "Content-Type": "application/json"
    }
    response = requests.get("https://api.xero.com/connections", headers=headers)

    if response.status_code == 200:
        connections = response.json()
        if connections:
            tokens['tenant_id'] = connections[0]['tenantId']
            with open('tokens.json', 'w') as file:
                json.dump(tokens, file, indent=2)
            print("Tenant ID saved successfully.")
        else:
            print("No connections found. Ensure your Xero account is linked to your app.")
    else:
        print(f"Failed to fetch tenant ID: {response.status_code} - {response.text}")

if __name__ == "__main__":
    fetch_and_save_tenant_id()
