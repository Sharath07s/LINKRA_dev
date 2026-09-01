"""add_canonical_entities

Revision ID: 1f5f437afa86
Revises: a3f7c8d92e14
Create Date: 2026-08-28 23:31:39.804772

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '1f5f437afa86'
down_revision: Union[str, Sequence[str], None] = 'a3f7c8d92e14'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create canonical_entities table
    op.create_table(
        'canonical_entities',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=1000), nullable=False),
        sa.Column('aliases', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('attributes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_canonical_entities_entity_type'), 'canonical_entities', ['entity_type'], unique=False)

    # Add columns to entity_candidates
    op.add_column('entity_candidates', sa.Column('resolved_to_id', sa.UUID(), nullable=True))
    op.add_column('entity_candidates', sa.Column('resolution_status', sa.String(length=50), server_default='UNRESOLVED', nullable=False))
    op.add_column('entity_candidates', sa.Column('resolution_score', sa.Float(), nullable=True))
    
    op.create_index(op.f('ix_entity_candidates_resolved_to_id'), 'entity_candidates', ['resolved_to_id'], unique=False)
    op.create_index(op.f('ix_entity_candidates_resolution_status'), 'entity_candidates', ['resolution_status'], unique=False)
    op.create_foreign_key(None, 'entity_candidates', 'canonical_entities', ['resolved_to_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop from entity_candidates
    op.drop_constraint(None, 'entity_candidates', type_='foreignkey')
    op.drop_index(op.f('ix_entity_candidates_resolution_status'), table_name='entity_candidates')
    op.drop_index(op.f('ix_entity_candidates_resolved_to_id'), table_name='entity_candidates')
    op.drop_column('entity_candidates', 'resolution_score')
    op.drop_column('entity_candidates', 'resolution_status')
    op.drop_column('entity_candidates', 'resolved_to_id')

    # Drop canonical_entities table
    op.drop_index(op.f('ix_canonical_entities_entity_type'), table_name='canonical_entities')
    op.drop_table('canonical_entities')
