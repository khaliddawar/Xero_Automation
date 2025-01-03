import pytest
from integration.xero.xero_client import XeroClient
from unittest.mock import Mock, patch

# Fixtures
@pytest.fixture
def xero_client():
    client = XeroClient()
    # Mock the authentication to avoid actual API calls
    client.authenticate = Mock()
    return client

@pytest.fixture
def invoice_data():
    return {
        'vendor_name': 'Test Vendor',
        'line_items': [{
            'description': 'Test Item',
            'quantity': 1,
            'unit_amount': 100.00
        }],
        'reference': 'INV-2024-001'
    }

@pytest.fixture
def contact_data():
    return {
        'name': 'Test Contact',
        'email': 'test@example.com',
        'phone': '+1234567890'
    }

# Tests
def test_create_invoice_success(xero_client, invoice_data):
    # Mock the Xero API response for success
    xero_client.xero = Mock()
    xero_client.xero.invoices.put = Mock(return_value={'InvoiceID': '123', 'Status': 'OK'})
    
    response = xero_client.create_invoice(invoice_data)
    
    assert response['InvoiceID'] == '123'
    assert response['Status'] == 'OK'
    xero_client.xero.invoices.put.assert_called_once()

def test_create_invoice_error(xero_client, invoice_data):
    # Mock the Xero API response for an error
    xero_client.xero = Mock()
    xero_client.xero.invoices.put = Mock(side_effect=Exception("Failed to create invoice"))
    
    with pytest.raises(Exception, match="Failed to create invoice"):
        xero_client.create_invoice(invoice_data)

def test_create_contact_success(xero_client, contact_data):
    # Mock the Xero API response for success
    xero_client.xero = Mock()
    xero_client.xero.contacts.put = Mock(return_value={'ContactID': '456', 'Status': 'OK'})
    
    response = xero_client.create_contact(contact_data)
    
    assert response['ContactID'] == '456'
    assert response['Status'] == 'OK'
    xero_client.xero.contacts.put.assert_called_once()

def test_create_contact_error(xero_client, contact_data):
    # Mock the Xero API response for an error
    xero_client.xero = Mock()
    xero_client.xero.contacts.put = Mock(side_effect=Exception("Failed to create contact"))
    
    with pytest.raises(Exception, match="Failed to create contact"):
        xero_client.create_contact(contact_data)

# Parameterized Test Example
@pytest.mark.parametrize("contact_data", [
    {'name': 'Contact 1', 'email': 'contact1@example.com', 'phone': '+1234567891'},
    {'name': 'Contact 2', 'email': 'contact2@example.com', 'phone': '+1234567892'},
    {'name': 'Contact 3', 'email': 'contact3@example.com', 'phone': '+1234567893'}
])
def test_create_multiple_contacts(xero_client, contact_data):
    xero_client.xero = Mock()
    xero_client.xero.contacts.put = Mock(return_value={'ContactID': '123', 'Status': 'OK'})
    
    response = xero_client.create_contact(contact_data)
    
    assert response['ContactID'] == '123'
    assert response['Status'] == 'OK'
    xero_client.xero.contacts.put.assert_called_once()
