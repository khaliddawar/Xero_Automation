import os
from datetime import datetime
import json
from typing import Dict, Any, Optional
from utils.config import config

class Storage:
    def __init__(self):
        self.base_path = config.STORAGE_PATH
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        """Ensure storage directories exist"""
        directories = [
            self.base_path,
            os.path.join(self.base_path, 'documents'),
            os.path.join(self.base_path, 'metadata'),
            os.path.join(self.base_path, 'processed')
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def save_document(self, document_id: str, content: bytes, metadata: Dict[str, Any]) -> str:
        """Save document content and metadata"""
        # Generate paths
        date_prefix = datetime.now().strftime('%Y/%m/%d')
        doc_path = os.path.join(self.base_path, 'documents', date_prefix)
        meta_path = os.path.join(self.base_path, 'metadata', date_prefix)
        
        # Create directories if they don't exist
        os.makedirs(doc_path, exist_ok=True)
        os.makedirs(meta_path, exist_ok=True)
        
        # Save document content
        doc_file = os.path.join(doc_path, f'{document_id}.bin')
        with open(doc_file, 'wb') as f:
            f.write(content)
        
        # Save metadata
        meta_file = os.path.join(meta_path, f'{document_id}.json')
        with open(meta_file, 'w') as f:
            json.dump(metadata, f)
        
        return doc_file
    
    def get_document(self, document_id: str, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Retrieve document content and metadata"""
        if date:
            date_prefix = date.strftime('%Y/%m/%d')
        else:
            # Search in recent directories
            base_dir = os.path.join(self.base_path, 'documents')
            for root, dirs, files in os.walk(base_dir):
                if f'{document_id}.bin' in files:
                    date_prefix = os.path.relpath(root, base_dir)
                    break
            else:
                raise FileNotFoundError(f"Document {document_id} not found")
        
        # Get document content
        doc_file = os.path.join(self.base_path, 'documents', date_prefix, f'{document_id}.bin')
        meta_file = os.path.join(self.base_path, 'metadata', date_prefix, f'{document_id}.json')
        
        if not os.path.exists(doc_file) or not os.path.exists(meta_file):
            raise FileNotFoundError(f"Document {document_id} not found")
        
        with open(doc_file, 'rb') as f:
            content = f.read()
            
        with open(meta_file, 'r') as f:
            metadata = json.load(f)
            
        return {
            'content': content,
            'metadata': metadata
        }
    
    def save_processed_results(self, document_id: str, results: Dict[str, Any]):
        """Save processing results"""
        date_prefix = datetime.now().strftime('%Y/%m/%d')
        proc_path = os.path.join(self.base_path, 'processed', date_prefix)
        os.makedirs(proc_path, exist_ok=True)
        
        proc_file = os.path.join(proc_path, f'{document_id}.json')
        with open(proc_file, 'w') as f:
            json.dump(results, f)
            
    def get_processed_results(self, document_id: str, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Retrieve processing results"""
        if date:
            date_prefix = date.strftime('%Y/%m/%d')
            proc_file = os.path.join(self.base_path, 'processed', date_prefix, f'{document_id}.json')
            
            if not os.path.exists(proc_file):
                raise FileNotFoundError(f"Processed results for document {document_id} not found")
                
            with open(proc_file, 'r') as f:
                return json.load(f)
        else:
            # Search in recent directories
            base_dir = os.path.join(self.base_path, 'processed')
            for root, dirs, files in os.walk(base_dir):
                if f'{document_id}.json' in files:
                    proc_file = os.path.join(root, f'{document_id}.json')
                    with open(proc_file, 'r') as f:
                        return json.load(f)
                        
            raise FileNotFoundError(f"Processed results for document {document_id} not found")