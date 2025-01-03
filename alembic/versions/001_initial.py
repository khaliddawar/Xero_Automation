"""Initial migration

Revision ID: 001
Create Date: 2024-01-15
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create processing_jobs table
    op.create_table(
        'processing_jobs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create processed_documents table
    op.create_table(
        'processed_documents',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('job_id', sa.String(), nullable=True),
        sa.Column('document_type', sa.String(), nullable=False),
        sa.Column('storage_path', sa.String(), nullable=False),
        sa.Column('processed_content', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('xero_reference', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['processing_jobs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('processed_documents')
    op.drop_table('processing_jobs')