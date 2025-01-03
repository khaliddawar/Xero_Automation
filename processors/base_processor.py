from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from models.document import Document

class BaseProcessor(ABC):
    """Base class for all processors"""
    
    @abstractmethod
    def process(self, document: Document) -> Dict[str, Any]:
        """Process a document and return results"""
        pass
    
    def validate_results(self, results: Dict[str, Any]) -> bool:
        """Validate processing results"""
        return True
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle processing errors"""
        return {
            'error': str(error),
            'status': 'failed'
        }
    
    def process_safe(self, document: Document) -> Dict[str, Any]:
        """Safely process a document with error handling"""
        try:
            results = self.process(document)
            if self.validate_results(results):
                return {
                    'status': 'success',
                    'results': results
                }
            else:
                return {
                    'status': 'validation_failed',
                    'error': 'Processing results failed validation'
                }
        except Exception as e:
            return self.handle_error(e)