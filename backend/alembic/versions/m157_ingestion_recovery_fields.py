"""add ingestion recovery fields

Revision ID: m157_recovery_fields
Revises: afda961488f7
Create Date: 2026-09-22 19:11:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'm157_recovery_fields'
down_revision: Union[str, None] = 'afda961488f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add recovery columns safely with defaults
    op.add_column('ingestion_jobs', sa.Column('failed_step', sa.String(length=100), nullable=True))
    op.add_column('ingestion_jobs', sa.Column('error_code', sa.String(length=100), nullable=True))
    op.add_column('ingestion_jobs', sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('ingestion_jobs', sa.Column('max_retry_count', sa.Integer(), nullable=False, server_default='3'))
    op.add_column('ingestion_jobs', sa.Column('last_retry_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('ingestion_jobs', sa.Column('next_retry_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('ingestion_jobs', sa.Column('failed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('ingestion_jobs', sa.Column('recovery_status', sa.String(length=50), nullable=False, server_default='NONE'))
    
    op.create_index(op.f('ix_ingestion_jobs_recovery_status'), 'ingestion_jobs', ['recovery_status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_ingestion_jobs_recovery_status'), table_name='ingestion_jobs')
    op.drop_column('ingestion_jobs', 'recovery_status')
    op.drop_column('ingestion_jobs', 'failed_at')
    op.drop_column('ingestion_jobs', 'next_retry_at')
    op.drop_column('ingestion_jobs', 'last_retry_at')
    op.drop_column('ingestion_jobs', 'max_retry_count')
    op.drop_column('ingestion_jobs', 'retry_count')
    op.drop_column('ingestion_jobs', 'error_code')
    op.drop_column('ingestion_jobs', 'failed_step')
