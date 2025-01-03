from datetime import datetime
from utils.config import config
from utils.logger import app_logger
import tempfile
import os
from .ms365_auth import MS365Auth

class EmailMonitor:
    def __init__(self):
        self.ms365 = MS365Auth()
        self.mailbox = None
        self.processed_emails = set()

    def connect(self):
        """Establish connection to Microsoft 365"""
        try:
            self.ms365.authenticate()
            self.mailbox = self.ms365.get_mailbox()
            app_logger.info("Successfully connected to Microsoft 365")
            return True
        except Exception as e:
            app_logger.error(f"Failed to connect to Microsoft 365: {str(e)}")
            raise

    def save_attachment(self, attachment, email_id):
        """Save email attachment to temporary file"""
        try:
            if attachment.name:
                # Create temp directory if it doesn't exist
                temp_dir = os.path.join(tempfile.gettempdir(), 'xero_automation')
                os.makedirs(temp_dir, exist_ok=True)
                
                filepath = os.path.join(temp_dir, f"{email_id}_{attachment.name}")
                
                # Download and save attachment
                attachment.save(filepath)
                app_logger.info(f"Saved attachment: {attachment.name}")
                return filepath
                
        except Exception as e:
            app_logger.error(f"Error saving attachment: {str(e)}")
        return None

    def check_new_emails(self):
        """Check for new unread emails"""
        try:
            if not self.mailbox:
                self.connect()

            # Get unread messages
            query = self.mailbox.new_query().on_attribute('isRead').equals(False)
            messages = self.mailbox.get_messages(query=query, limit=10)
            
            new_emails = []
            for message in messages:
                if message.object_id not in self.processed_emails:
                    try:
                        attachments = []
                        
                        # Process attachments
                        for attachment in message.attachments:
                            filepath = self.save_attachment(attachment, message.object_id)
                            if filepath:
                                attachments.append(filepath)
                        
                        email_data = {
                            'id': message.object_id,
                            'subject': message.subject,
                            'sender': message.sender.address,
                            'date': message.received.strftime('%Y-%m-%d %H:%M:%S'),
                            'body': message.body,
                            'attachments': attachments
                        }
                        
                        new_emails.append(email_data)
                        self.processed_emails.add(message.object_id)
                        app_logger.info(f"Found new email: {email_data['subject']}")
                        
                        # Mark as read
                        message.mark_as_read()
                        
                    except Exception as e:
                        app_logger.error(f"Error processing message {message.object_id}: {str(e)}")
            
            if not new_emails:
                app_logger.info("No new emails found")
            
            return new_emails
            
        except Exception as e:
            app_logger.error(f"Error checking new emails: {str(e)}")
            return []

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass  # OAuth2 doesn't need explicit disconnection