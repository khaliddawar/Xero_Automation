from integration.xero.xero_client import XeroClient
from datetime import datetime, timedelta

def test_create_invoice():
    try:
        print("\nStarting invoice creation test...")
        print("-" * 50)
        
        # Initialize and authenticate
        client = XeroClient()
        client.authenticate()
        
        # Prepare invoice data
        tomorrow = datetime.now() + timedelta(days=1)
        
        invoice_data = {
            "Type": "ACCPAY",
            "Contact": {
                "Name": "Test Supplier"
            },
            "LineItems": [
                {
                    "Description": "Test Item",
                    "Quantity": 1.0,
                    "UnitAmount": 100.00,
                    "AccountCode": "200"
                }
            ],
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "DueDate": tomorrow.strftime("%Y-%m-%d"),
            "Reference": "TEST-001",
            "Status": "DRAFT"
        }
        
        print("\nCreating test invoice...")
        response = client.create_invoice(invoice_data)
        
        print("\nInvoice created successfully!")
        print(f"Invoice ID: {response.get('InvoiceID')}")
        print(f"Invoice Number: {response.get('InvoiceNumber')}")
        print(f"Status: {response.get('Status')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Invoice creation failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_create_invoice()