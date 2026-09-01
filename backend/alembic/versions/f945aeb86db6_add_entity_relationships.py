"""add_entity_relationships

Revision ID: f945aeb86db6
Revises: 1f5f437afa86
Create Date: 2026-08-28 23:57:23.415171

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f945aeb86db6'
down_revision: Union[str, Sequence[str], None] = '1f5f437afa86'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'entity_relationships',
        sa.Column('id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('source_entity_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('target_entity_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('relationship_type', sa.String(length=100), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('extraction_method', sa.String(length=50), nullable=False),
        sa.Column('ingestion_job_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('source_page', sa.Integer(), nullable=True),
        sa.Column('source_row', sa.Integer(), nullable=True),
        sa.Column('event_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['ingestion_job_id'], ['ingestion_jobs.id'], ),
        sa.ForeignKeyConstraint(['source_entity_id'], ['canonical_entities.id'], ),
        sa.ForeignKeyConstraint(['target_entity_id'], ['canonical_entities.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_entity_id', 'target_entity_id', 'relationship_type', 'ingestion_job_id', 'source_page', 'source_row', 'event_timestamp', name='_uniq_relationship_event')
    )
    op.create_index(op.f('ix_entity_relationships_id'), 'entity_relationships', ['id'], unique=False)
    op.create_index(op.f('ix_entity_relationships_source_entity_id'), 'entity_relationships', ['source_entity_id'], unique=False)
    op.create_index(op.f('ix_entity_relationships_target_entity_id'), 'entity_relationships', ['target_entity_id'], unique=False)
    op.create_index(op.f('ix_entity_relationships_relationship_type'), 'entity_relationships', ['relationship_type'], unique=False)
    op.create_index(op.f('ix_entity_relationships_ingestion_job_id'), 'entity_relationships', ['ingestion_job_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_entity_relationships_ingestion_job_id'), table_name='entity_relationships')
    op.drop_index(op.f('ix_entity_relationships_relationship_type'), table_name='entity_relationships')
    op.drop_index(op.f('ix_entity_relationships_target_entity_id'), table_name='entity_relationships')
    op.drop_index(op.f('ix_entity_relationships_source_entity_id'), table_name='entity_relationships')
    op.drop_index(op.f('ix_entity_relationships_id'), table_name='entity_relationships')
    op.drop_table('entity_relationships')
