import msal
import requests
from utils.config import config
import base64
import os
from datetime import datetime
import tempfile

class MS365Auth:
    def __init__(self):
        self.client_id = config.MS365_CLIENT_ID
        self.client_secret = config.MS365_CLIENT_SECRET
        self.tenant_id = config.MS365_TENANT_ID
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scope = ["https://graph.microsoft.com/.default"]
        
        # Initialize MSAL application
        self.app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=self.authority
        )

    def authenticate(self):
        try:
            print("\nAttempting to acquire token...")
            result = self.app.acquire_token_silent(self.scope, account=None)
            
            if not result:
                print("No token in cache, acquiring new token...")
                result = self.app.acquire_token_for_client(scopes=self.scope)
            
            if "access_token" in result:
                print("✓ Token acquired successfully!")
                self.access_token = result['access_token']
                return True
            else:
                print(f"Error acquiring token: {result.get('error')}")
                print(f"Error description: {result.get('error_description')}")
                return False
                
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return False

    def get_messages_with_attachments(self, limit=10):
        """Get messages that have attachments"""
        try:
            if not hasattr(self, 'access_token'):
                if not self.authenticate():
                    raise Exception("Failed to authenticate")
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Get unread messages
            user_id = config.MS365_USER
            url = f"https://graph.microsoft.com/v1.0/users/{user_id}/messages"
            
            params = {
                '$top': 50,  # Get more messages to filter from
                '$orderby': 'receivedDateTime desc',
                '$select': 'id,subject,from,receivedDateTime,hasAttachments,isRead'
            }
            
            print(f"\nChecking recent messages...")
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                all_messages = response.json().get('value', [])
                # Filter messages with attachments
                messages_with_attachments = [
                    msg for msg in all_messages 
                    if msg.get('hasAttachments', False) and not msg.get('isRead', True)
                ]
                # Limit the results
                return messages_with_attachments[:limit]
            else:
                print(f"Error getting messages: {response.status_code}")
                print(f"Response: {response.text}")
                return []
                
        except Exception as e:
            print(f"Error getting messages: {str(e)}")
            return []

    def get_message_attachments(self, message_id):
        """Get attachments for a specific message"""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            user_id = config.MS365_USER
            url = f"https://graph.microsoft.com/v1.0/users/{user_id}/messages/{message_id}/attachments"
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                attachments = response.json().get('value', [])
                print(f"Found {len(attachments)} attachments")
                return attachments
            else:
                print(f"Error getting attachments: {response.status_code}")
                print(f"Response: {response.text}")
                return []
                
        except Exception as e:
            print(f"Error getting attachments: {str(e)}")
            return []

    def download_attachment(self, message_id, attachment):
        """Download and save an attachment"""
        try:
            # Create temp directory if it doesn't exist
            temp_dir = os.path.join(tempfile.gettempdir(), 'xero_automation')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Get attachment content
            content_bytes = base64.b64decode(attachment['contentBytes'])
            
            # Save to file
            filename = attachment['name']
            filepath = os.path.join(temp_dir, f"{message_id}_{filename}")
            
            with open(filepath, 'wb') as f:
                f.write(content_bytes)
            
            print(f"Saved attachment to: {filepath}")    
            return filepath
            
        except Exception as e:
            print(f"Error downloading attachment: {str(e)}")
            return None

    def mark_as_read(self, message_id):
        """Mark a message as read"""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            user_id = config.MS365_USER
            url = f"https://graph.microsoft.com/v1.0/users/{user_id}/messages/{message_id}"
            
            data = {
                "isRead": True
            }
            
            response = requests.patch(url, headers=headers, json=data)
            
            if response.status_code == 200:
                print(f"Message marked as read")
                return True
            else:
                print(f"Error marking message as read: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error marking message as read: {str(e)}")
            return False