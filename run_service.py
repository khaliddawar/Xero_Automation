from services.monitor_service import MonitorService
from utils.logger import app_logger
import signal
import sys
import time

class ServiceRunner:
    def __init__(self):
        self.service = MonitorService()
        self.running = False
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print("\nShutdown signal received. Stopping service...")
        self.running = False

    def run(self, check_interval=300):  # 5 minutes default
        """Run the service continuously"""
        self.running = True
        
        print("\nXero Automation Service")
        print("=" * 50)
        print(f"Check interval: {check_interval} seconds")
        print("\nService is running...")
        print("Press Ctrl+C to stop")
        
        while self.running:
            try:
                self.service.process_emails()
                
                # Show a simple activity indicator
                for _ in range(min(check_interval, 5)):  # Show max 5 dots
                    if not self.running:
                        break
                    sys.stdout.write(".")
                    sys.stdout.flush()
                    time.sleep(1)
                    
                if check_interval > 5:
                    time.sleep(check_interval - 5)
                
                sys.stdout.write("\r" + " " * 10 + "\r")  # Clear the dots
                
            except Exception as e:
                app_logger.error(f"Error in service: {str(e)}")
                time.sleep(check_interval)

        print("\nService stopped.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Xero Automation Service')
    parser.add_argument(
        '--interval', 
        type=int, 
        default=300,
        help='Check interval in seconds (default: 300)'
    )
    
    args = parser.parse_args()
    
    runner = ServiceRunner()
    runner.run(args.interval)