"""M16_intelligence_taxonomy

Revision ID: d21fb9ede316
Revises: m1571_durable_source_metadata
Create Date: 2026-09-23 04:16:58.851164

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd21fb9ede316'
down_revision: Union[str, Sequence[str], None] = 'm1571_durable_source_metadata'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('entity_relationships', sa.Column('status', sa.String(length=50), server_default='CONFIRMED', nullable=False))

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('entity_relationships', 'status')
