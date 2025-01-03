from integration.xero.xero_client import XeroClient

def test_xero():
    print("\nTesting Xero Connection")
    print("=" * 50)
    
    try:
        # Initialize client
        print("\n1. Initializing Xero client...")
        client