"""M15.4: Update document_chunks for provenance and RAG

Revision ID: m154_document_rag
Revises: 1fb69dab13ab
Create Date: 2026-09-22

Updates the document_chunks table with proper provenance fields:
- ingestion_job_id (FK to ingestion_jobs)
- chunk_index, chunk_text, page_number, source_row
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector.sqlalchemy


# revision identifiers, used by Alembic.
revision: str = 'm154_document_rag'
down_revision: Union[str, Sequence[str], None] = '1fb69dab13ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Update schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # Add new columns
    op.add_column('document_chunks', sa.Column('ingestion_job_id', sa.Uuid(), nullable=True))
    op.add_column('document_chunks', sa.Column('chunk_index', sa.Integer(), server_default='0', nullable=False))
    op.add_column('document_chunks', sa.Column('chunk_text', sa.Text(), nullable=True))
    op.add_column('document_chunks', sa.Column('page_number', sa.Integer(), nullable=True))
    op.add_column('document_chunks', sa.Column('source_row', sa.Integer(), nullable=True))

    # Copy data if there is any (unlikely based on audit, but safe to do)
    op.execute("UPDATE document_chunks SET chunk_text = content")

    # Now make chunk_text non-nullable
    op.alter_column('document_chunks', 'chunk_text', nullable=False)
    
    # Drop old columns and indices
    op.drop_index('ix_document_chunks_source_id', table_name='document_chunks')
    op.drop_column('document_chunks', 'content')
    op.drop_column('document_chunks', 'source_id')

    # Add new constraints and indices
    op.create_foreign_key('fk_document_chunks_ingestion_job_id', 'document_chunks', 'ingestion_jobs', ['ingestion_job_id'], ['id'])
    op.create_index(op.f('ix_document_chunks_ingestion_job_id'), 'document_chunks', ['ingestion_job_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('document_chunks', sa.Column('source_id', sa.String(length=255), nullable=True))
    op.add_column('document_chunks', sa.Column('content', sa.Text(), nullable=True))

    op.execute("UPDATE document_chunks SET content = chunk_text")
    op.alter_column('document_chunks', 'content', nullable=False)

    op.drop_index(op.f('ix_document_chunks_ingestion_job_id'), table_name='document_chunks')
    op.drop_constraint('fk_document_chunks_ingestion_job_id', 'document_chunks', type_='foreignkey')

    op.drop_column('document_chunks', 'source_row')
    op.drop_column('document_chunks', 'page_number')
    op.drop_column('document_chunks', 'chunk_text')
    op.drop_column('document_chunks', 'chunk_index')
    op.drop_column('document_chunks', 'ingestion_job_id')

    op.create_index('ix_document_chunks_source_id', 'document_chunks', ['source_id'], unique=False)
