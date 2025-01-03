import imaplib
import email
from email.message import EmailMessage
from typing import List, Dict, Any, Optional
import os
from datetime import datetime
from utils.config import config

class EmailHandler:
    def __init__(self):
        self.server = config.EMAIL_SERVER
        self.user = config.EMAIL_USER
        self.password = config.EMAIL_PASSWORD
        self.conn = None

    def connect(self):
        """Establish connection to email server"""
        try:
            self.conn = imaplib.IMAP4_SSL(self.server)
            self.conn.login(self.user, self.password)
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to email server: {str(e)}")

    def disconnect(self):
        """Close connection to email server"""
        if self.conn:
            try:
                self.conn.logout()
            except:
                pass

    def _extract_attachments(self, msg: EmailMessage) -> List[Dict[str, Any]]:
        """Extract attachments from email message"""
        attachments = []
        
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()
            if filename:
                # Get file content
                content = part.get_payload(decode=True)
                attachments.append({
                    'filename': filename,
                    'content': content,
                    'content_type': part.get_content_type()
                })

        return attachments

    def process_email(self, email_id: str) -> Dict[str, Any]:
        """Process a single email and return standardized format"""
        try:
            _, msg_data = self.conn.fetch(email_id, '(RFC822)')
            email_body = msg_data[0][1]
            msg = email.message_from_bytes(email_body)

            # Extract text content
            text_content = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        text_content += part.get_payload(decode=True).decode()
            else:
                text_content = msg.get_payload(decode=True).decode()

            # Extract attachments
            attachments = self._extract_attachments(msg)

            return {
                'source': 'email',
                'subject': msg['subject'],
                'text': text_content,
                'sender': msg['from'],
                'timestamp': msg['date'],
                'attachments': attachments,
                'metadata': {
                    'to': msg['to'],
                    'cc': msg.get('cc', ''),
                    'message_id': msg['message-id']
                }
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to process email {email_id}: {str(e)}")

    def get_unread_messages(self) -> List[Dict[str, Any]]:
        """Retrieve and process all unread messages"""
        messages = []
        
        try:
            self.conn.select('INBOX')
            _, message_numbers = self.conn.search(None, 'UNSEEN')
            
            for num in message_numbers[0].split():
                message = self.process_email(num)
                messages.append(message)
                
            return messages
        
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve unread messages: {str(e)}")
        
    def __enter__(self):
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()