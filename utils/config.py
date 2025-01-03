import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Tesseract Configuration
    TESSERACT_PATH = os.getenv('TESSERACT_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
    
    # Email Provider Configuration
    EMAIL_PROVIDER = os.getenv('EMAIL_PROVIDER', 'Microsoft365')
    
    # Gmail Configuration
    GMAIL_SERVER = os.getenv('GMAIL_SERVER', 'imap.gmail.com')
    GMAIL_USER = os.getenv('GMAIL_USER')
    GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')
    
    # Microsoft 365 Configuration
    MS365_CLIENT_ID = os.getenv('MS365_CLIENT_ID')
    MS365_CLIENT_SECRET = os.getenv('MS365_CLIENT_SECRET')
    MS365_TENANT_ID = os.getenv('MS365_TENANT_ID')
    MS365_USER = os.getenv('MS365_USER')
    
    # Active Email Configuration (based on provider)
    @property
    def EMAIL_SERVER(self):
        return 'outlook.office365.com' if self.EMAIL_PROVIDER == 'Microsoft365' else self.GMAIL_SERVER
    
    @property
    def EMAIL_USER(self):
        return self.MS365_USER if self.EMAIL_PROVIDER == 'Microsoft365' else self.GMAIL_USER
    
    @property
    def EMAIL_PASSWORD(self):
        return self.MS365_CLIENT_SECRET if self.EMAIL_PROVIDER == 'Microsoft365' else self.GMAIL_PASSWORD
    
    # Xero Configuration
    XERO_CLIENT_ID = os.getenv('XERO_CLIENT_ID')
    XERO_CLIENT_SECRET = os.getenv('XERO_CLIENT_SECRET')
    XERO_TENANT_ID = os.getenv('XERO_TENANT_ID')
    
    # Storage Configuration
    STORAGE_PATH = os.getenv('STORAGE_PATH', 'storage')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @staticmethod
    def validate():
        """Validate required configuration values"""
        config = Config()
        
        # Validate Xero configuration
        if not all([config.XERO_CLIENT_ID, config.XERO_CLIENT_SECRET]):
            raise ValueError("Missing required Xero credentials")
            
        # Validate email configuration based on provider
        if config.EMAIL_PROVIDER == 'Microsoft365':
            if not all([config.MS365_CLIENT_ID, config.MS365_CLIENT_SECRET, config.MS365_USER]):
                raise ValueError("Missing Microsoft 365 credentials. Please set MS365_CLIENT_ID, MS365_CLIENT_SECRET, and MS365_USER")
        else:  # Gmail
            if not all([config.GMAIL_USER, config.GMAIL_PASSWORD]):
                raise ValueError("Missing Gmail credentials")

config = Config()