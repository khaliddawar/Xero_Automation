from integration.xero.xero_client import XeroClient
import json

def print_org_settings():
    client = XeroClient()
    
    if not client.ensure_token_valid():
        print("Please authenticate first by running the OAuth server")
        return
        
    print("\nRetrieving Xero organization settings...")
    
    # Get organization details
    org = client.get_organisation_settings()
    if org:
        print("\nOrganization Details:")
        print(f"Name: {org.get('Name')}")
        print(f"Default Currency: {org.get('BaseCurrency')}")
        print(f"Organisation Type: {org.get('OrganisationType')}")
        print(f"Tax Numbers: {org.get('TaxNumbers', [])}")
        
    # Get tax rates
    tax_rates = client.get_tax_rates()
    if tax_rates:
        print("\nAvailable Tax Rates:")
        for rate in tax_rates:
            print(f"Name: {rate.get('Name')}")
            print(f"Tax Type: {rate.get('TaxType')}")
            print(f"Rate: {rate.get('EffectiveRate')}%")
            print("---")
            
    # Get accounts
    accounts = client.get_chart_of_accounts()
    if accounts:
        print("\nChart of Accounts:")
        for account in accounts:
            if account.get('Status') == 'ACTIVE':
                print(f"Code: {account.get('Code')}")
                print(f"Name: {account.get('Name')}")
                print(f"Type: {account.get('Type')}")
                print(f"Tax Type: {account.get('TaxType', 'N/A')}")
                print("---")

if __name__ == "__main__":
    print_org_settings()