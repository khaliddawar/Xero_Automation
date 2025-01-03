def fetch_contacts():
    with open('tokens.json', 'r') as file:
        tokens = json.load(file)

    headers = {
        "Authorization": f"Bearer {tokens['access_token']}",
        "Xero-tenant-id": tokens['tenant_id'],
        "Content-Type": "application/json"
    }

    response = requests.get("https://api.xero.com/api.xro/2.0/Contacts", headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")

    if response.status_code == 200:
        contacts = response.json()
        print(json.dumps(contacts, indent=2))
        return contacts
    else:
        print("Failed to fetch contacts.")
        return None
