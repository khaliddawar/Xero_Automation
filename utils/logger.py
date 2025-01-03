import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
from utils.config import config

class Logger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, config.LOG_LEVEL.upper()))
        
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        # Create formatters and handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        file_handler = RotatingFileHandler(
            f'logs/{name}.log',
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def error(self, message: str, exc_info=True):
        """Log error message"""
        self.logger.error(message, exc_info=exc_info)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)

# Create main application logger
app_logger = Logger('xero_automation')