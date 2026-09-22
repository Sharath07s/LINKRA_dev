"""add durable source storage metadata to ingestion_jobs

Revision ID: m1571_durable_source_metadata
Revises: m157_recovery_fields
Create Date: 2026-09-22 21:00:00.000000

Adds the durable source storage fields introduced in M15.7.1.
All new columns are nullable (with no server_default) to ensure
full backward compatibility with existing ingestion_jobs rows
that were created before this migration.

Columns added:
    source_storage_provider  VARCHAR(50)    NULL — 'local' | 'supabase'
    source_storage_key       VARCHAR(1000)  NULL — object key / path in storage
    source_original_filename VARCHAR(500)   NULL — original user filename
    source_content_type      VARCHAR(200)   NULL — MIME type
    source_size_bytes        BIGINT         NULL — byte count of original source
    source_sha256            VARCHAR(64)    NULL — hex SHA-256 checksum
    source_storage_bucket    VARCHAR(200)   NULL — bucket name (Supabase / S3)
    source_uploaded_at       TIMESTAMPTZ    NULL — when durable upload completed

Index:
    ix_ingestion_jobs_source_storage_key on source_storage_key
        (for fast lookup during retry restoration)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'm1571_durable_source_metadata'
down_revision: Union[str, None] = 'm157_recovery_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add durable source storage columns — all nullable for backward compat
    op.add_column('ingestion_jobs', sa.Column('source_storage_provider', sa.String(length=50), nullable=True))
    op.add_column('ingestion_jobs', sa.Column('source_storage_key', sa.String(length=1000), nullable=True))
    op.add_column('ingestion_jobs', sa.Column('source_original_filename', sa.String(length=500), nullable=True))
    op.add_column('ingestion_jobs', sa.Column('source_content_type', sa.String(length=200), nullable=True))
    op.add_column('ingestion_jobs', sa.Column('source_size_bytes', sa.BigInteger(), nullable=True))
    op.add_column('ingestion_jobs', sa.Column('source_sha256', sa.String(length=64), nullable=True))
    op.add_column('ingestion_jobs', sa.Column('source_storage_bucket', sa.String(length=200), nullable=True))
    op.add_column('ingestion_jobs', sa.Column('source_uploaded_at', sa.DateTime(timezone=True), nullable=True))

    # Index for fast lookup of jobs by their storage key (used during retry restoration)
    op.create_index(
        op.f('ix_ingestion_jobs_source_storage_key'),
        'ingestion_jobs',
        ['source_storage_key'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_ingestion_jobs_source_storage_key'), table_name='ingestion_jobs')
    op.drop_column('ingestion_jobs', 'source_uploaded_at')
    op.drop_column('ingestion_jobs', 'source_storage_bucket')
    op.drop_column('ingestion_jobs', 'source_sha256')
    op.drop_column('ingestion_jobs', 'source_size_bytes')
    op.drop_column('ingestion_jobs', 'source_content_type')
    op.drop_column('ingestion_jobs', 'source_original_filename')
    op.drop_column('ingestion_jobs', 'source_storage_key')
    op.drop_column('ingestion_jobs', 'source_storage_provider')
