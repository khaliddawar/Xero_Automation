from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class Document:
    """Represents a document (invoice, receipt, etc.)"""
    id: str
    source: str  # email, whatsapp, clickup
    content_type: str  # pdf, image, text
    raw_content: bytes
    processed_content: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary"""
        return {
            'id': self.id,
            'source': self.source,
            'content_type': self.content_type,
            'processed_content': self.processed_content,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create document from dictionary"""
        return cls(
            id=data['id'],
            source=data['source'],
            content_type=data['content_type'],
            raw_content=data.get('raw_content', b''),
            processed_content=data['processed_content'],
            metadata=data.get('metadata', {}),
            created_at=datetime.fromisoformat(data['created_at']),
            processed_at=datetime.fromisoformat(data['processed_at']) if data.get('processed_at') else None
        )