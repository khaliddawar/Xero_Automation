import pytest
from input_handlers.message_handler import WhatsAppHandler, ClickUpHandler
from datetime import datetime

@pytest.fixture
def whatsapp_message():
    return {
        'text': 'Invoice for project ABC: $500',
        'from': '+1234567890',
        'timestamp': datetime.now().isoformat(),
        'type': 'text',
    }

@pytest.fixture
def clickup_message():
    return {
        'description': 'Please process invoice attached',
        'creator': {'username': 'john.doe'},
        'date_created': datetime.now().isoformat(),
        'attachments': [
            {'name': 'invoice.pdf', 'url': 'http://example.com/invoice.pdf'}
        ]
    }

def test_whatsapp_handler(whatsapp_message):
    handler = WhatsAppHandler()
    result = handler.process_message(whatsapp_message)
    
    assert result['source'] == 'whatsapp'
    assert result['text'] == whatsapp_message['text']
    assert result['sender'] == whatsapp_message['from']
    assert 'timestamp' in result
    assert 'metadata' in result

def test_clickup_handler(clickup_message):
    handler = ClickUpHandler()
    result = handler.process_message(clickup_message)
    
    assert result['source'] == 'clickup'
    assert result['text'] == clickup_message['description']
    assert result['sender'] == clickup_message['creator']['username']
    assert len(result['attachments']) == 1
    assert result['attachments'][0]['name'] == 'invoice.pdf'