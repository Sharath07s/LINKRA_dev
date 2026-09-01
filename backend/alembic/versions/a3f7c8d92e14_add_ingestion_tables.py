"""add_ingestion_tables

Revision ID: a3f7c8d92e14
Revises: 6ebe98bc6b0e
Create Date: 2026-08-28 23:00:00.000000

Adds ingestion_jobs and entity_candidates tables for M1.3 data ingestion pipeline.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3f7c8d92e14'
down_revision: Union[str, Sequence[str], None] = '6ebe98bc6b0e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create ingestion_jobs and entity_candidates tables."""
    op.create_table(
        'ingestion_jobs',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('file_name', sa.String(500), nullable=False),
        sa.Column('source_type', sa.String(100), nullable=False),
        sa.Column('file_type', sa.String(20), nullable=False),
        sa.Column('file_size_bytes', sa.Integer, nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='QUEUED'),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('record_count', sa.Integer, nullable=True),
        sa.Column('entity_count', sa.Integer, nullable=True),
        sa.Column('uploaded_by', sa.Uuid(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        # BaseModel mixins
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Uuid(as_uuid=True), nullable=True),
        sa.Column('updated_by', sa.Uuid(as_uuid=True), nullable=True),
    )
    op.create_index('ix_ingestion_jobs_status', 'ingestion_jobs', ['status'])

    op.create_table(
        'entity_candidates',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('ingestion_job_id', sa.Uuid(as_uuid=True), sa.ForeignKey('ingestion_jobs.id'), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('raw_text', sa.String(1000), nullable=False),
        sa.Column('normalized_value', sa.String(1000), nullable=True),
        sa.Column('confidence', sa.Float, nullable=True),
        sa.Column('source_page', sa.Integer, nullable=True),
        sa.Column('source_row', sa.Integer, nullable=True),
        sa.Column('start_offset', sa.Integer, nullable=True),
        sa.Column('end_offset', sa.Integer, nullable=True),
        sa.Column('extraction_method', sa.String(50), nullable=False),
        # BaseModel mixins
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Uuid(as_uuid=True), nullable=True),
        sa.Column('updated_by', sa.Uuid(as_uuid=True), nullable=True),
    )
    op.create_index('ix_entity_candidates_ingestion_job_id', 'entity_candidates', ['ingestion_job_id'])
    op.create_index('ix_entity_candidates_entity_type', 'entity_candidates', ['entity_type'])


def downgrade() -> None:
    """Drop ingestion_jobs and entity_candidates tables."""
    op.drop_index('ix_entity_candidates_entity_type', table_name='entity_candidates')
    op.drop_index('ix_entity_candidates_ingestion_job_id', table_name='entity_candidates')
    op.drop_table('entity_candidates')
    op.drop_index('ix_ingestion_jobs_status', table_name='ingestion_jobs')
    op.drop_table('ingestion_jobs')
