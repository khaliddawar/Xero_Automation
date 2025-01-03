def create_invoice():
    print("Starting invoice creation...")
    try:
        access_token, tenant_id = load_tokens()
        print("Tokens Loaded:", access_token, tenant_id)
        
        url = "https://api.xero.com/api.xro/2.0/Invoices"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Xero-tenant-id": tenant_id,
        }
        payload = {
            "Type": "ACCREC",
            "Contact": {
                "ContactID": "9800277c-62cc-4367-b06e-68f1e0518f36"  # Replace with a valid ContactID
            },
            "Date": "2025-01-03",
            "DueDate": "2025-01-10",
            "LineItems": [
                {
                    "Description": "Sample Item",
                    "Quantity": 1,
                    "UnitAmount": 100.00,
                    "AccountCode": "200"  # Replace with a valid account code
                }
            ],
            "Status": "DRAFT"
        }
        
        print("Sending request to Xero API...")
        response = requests.post(url, headers=headers, json=payload)
        
        print("Response Status Code:", response.status_code)
        print("Raw Response Text:", response.text)
        
        if response.status_code == 200 or response.status_code == 201:
            print("Invoice created successfully!")
            try:
                response_data = response.json()
                print("Invoice Details:", response_data)
            except ValueError:
                print("Error: Invalid JSON response from the API.")
                print("Raw Response:", response.text)
        else:
            print(f"Failed to create invoice. Status Code: {response.status_code}")
            print("Response Text:", response.text)
    except Exception as e:
        print("An error occurred:", str(e))
