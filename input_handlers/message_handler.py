from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

class MessageHandler(ABC):
    """Abstract base class for message handlers"""
    
    @abstractmethod
    def process_message(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming message and return standardized format"""
        pass

class WhatsAppHandler(MessageHandler):
    """Handler for WhatsApp messages"""
    
    def process_message(self, content: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'source': 'whatsapp',
            'text': content.get('text', ''),
            'sender': content.get('from', ''),
            'timestamp': content.get('timestamp', datetime.now().isoformat()),
            'attachments': content.get('attachments', []),
            'metadata': {
                'phone_number': content.get('from', ''),
                'message_type': content.get('type', 'text')
            }
        }

class ClickUpHandler(MessageHandler):
    """Handler for ClickUp messages/tasks"""
    
    def process_message(self, content: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'source': 'clickup',
            'text': content.get('description', ''),
            'sender': content.get('creator', {}).get('username', ''),
            'timestamp': content.get('date_created', datetime.now().isoformat()),
            'attachments': [
                {
                    'name': attachment.get('name', ''),
                    'url': attachment.get('url', '')
                }
                for attachment in content.get('attachments', [])
            ],
            'metadata': {
                'task_id': content.get('id'),
                'list_id': content.get('list', {}).get('id'),
                'status': content.get('status', {}).get('status')
            }
        }

def get_message_handler(source: str) -> MessageHandler:
    """Factory function to get appropriate message handler"""
    handlers = {
        'whatsapp': WhatsAppHandler,
        'clickup': ClickUpHandler
    }
    
    handler_class = handlers.get(source.lower())
    if not handler_class:
        raise ValueError(f"Unsupported message source: {source}")
    
    return handler_class()