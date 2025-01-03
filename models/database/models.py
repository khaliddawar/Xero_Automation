from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from datetime import datetime

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(String, primary_key=True)
    source = Column(String, nullable=False)
    status = Column(String, nullable=False)  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    error_message = Column(String, nullable=True)
    metadata = Column(JSON, nullable=True)

class ProcessedDocument(Base):
    __tablename__ = "processed_documents"

    id = Column(String, primary_key=True)
    job_id = Column(String, ForeignKey('processing_jobs.id'))
    document_type = Column(String, nullable=False)  # invoice, receipt, etc.
    storage_path = Column(String, nullable=False)
    processed_content = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    xero_reference = Column(String, nullable=True)

    # Relationship
    job = relationship("ProcessingJob", backref="documents")