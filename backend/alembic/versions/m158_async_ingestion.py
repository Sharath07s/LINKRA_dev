"""M15.8 async ingestion progress tracking

Revision ID: m158_async_ingestion
Revises: d21fb9ede316
Create Date: 2026-09-23 04:49:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'm158_async_ingestion'
down_revision: Union[str, Sequence[str], None] = 'd21fb9ede316'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add M15.8 async pipeline progress tracking fields."""
    op.add_column('ingestion_jobs', sa.Column('current_step', sa.String(length=100), nullable=True))
    op.add_column('ingestion_jobs', sa.Column('relationship_count', sa.Integer(), nullable=True))
    op.add_column('ingestion_jobs', sa.Column('progress_detail', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Remove M15.8 async pipeline progress tracking fields."""
    op.drop_column('ingestion_jobs', 'progress_detail')
    op.drop_column('ingestion_jobs', 'relationship_count')
    op.drop_column('ingestion_jobs', 'current_step')
