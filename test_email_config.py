from utils.config import config
from services.email_monitor import EmailMonitor

def test_email_config():
    print("\nEmail Configuration Test")
    print("=" * 50)
    
    # Show current configuration
    print(f"\nCurrent Provider: {config.EMAIL_PROVIDER}")
    print(f"Active Server  : {config.EMAIL_SERVER}")
    print(f"Active User   : {config.EMAIL_USER}")
    
    # Show available configurations
    print("\nAvailable Configurations:")
    print("\nGmail Settings:")
    print(f"  Server  : {config.GMAIL_SERVER}")
    print(f"  User    : {config.GMAIL_USER}")
    print(f"  Password: {'*' * len(config.GMAIL_PASSWORD) if config.GMAIL_PASSWORD else 'Not Set'}")
    
    print("\nMicrosoft 365 Settings:")
    print(f"  Server  : {config.MS365_SERVER}")
    print(f"  User    : {config.MS365_USER}")
    print(f"  Password: {'*' * len(config.MS365_PASSWORD) if config.MS365_PASSWORD else 'Not Set'}")
    
    # Test connection
    print("\nTesting email connection...")
    try:
        with EmailMonitor() as monitor:
            print("✓ Successfully connected to email server")
            print(f"✓ Connected to: {monitor.email_server}")
            print(f"✓ Using account: {monitor.email_user}")
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")

if __name__ == "__main__":
    test_email_config()