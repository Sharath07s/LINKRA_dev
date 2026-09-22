"""Merge multiple heads for M15.4

Revision ID: afda961488f7
Revises: d4b2e8f1a305, m154_document_rag
Create Date: 2026-09-22 13:35:16.343941

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'afda961488f7'
down_revision: Union[str, Sequence[str], None] = ('d4b2e8f1a305', 'm154_document_rag')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
