"""create evidence_links table

Revision ID: d4b2e8f1a305
Revises: c3a1d7e8f204
Create Date: 2026-09-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import ProgrammingError

revision: str = 'd4b2e8f1a305'
down_revision: Union[str, None] = 'c3a1d7e8f204'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    try:
        with op.get_bind().begin_nested():
            op.create_table(
                'evidence_links',
                sa.Column('id', sa.Uuid(), nullable=False),
                sa.Column('relationship_id', sa.Uuid(), nullable=True),
                sa.Column('candidate_id', sa.Uuid(), nullable=True),
                sa.Column('document_chunk_id', sa.Uuid(), nullable=False),
                sa.Column('char_start', sa.Integer(), nullable=True),
                sa.Column('char_end', sa.Integer(), nullable=True),
                sa.Column('quote_snippet', sa.Text(), nullable=False),
                sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
                sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
                sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
                sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
                sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
                sa.Column('created_by', sa.Uuid(), nullable=True),
                sa.Column('updated_by', sa.Uuid(), nullable=True),
                sa.ForeignKeyConstraint(['relationship_id'], ['entity_relationships.id'], ondelete='CASCADE'),
                sa.ForeignKeyConstraint(['candidate_id'], ['entity_candidates.id'], ondelete='CASCADE'),
                sa.ForeignKeyConstraint(['document_chunk_id'], ['document_chunks.id'], ondelete='CASCADE'),
                sa.PrimaryKeyConstraint('id')
            )
            op.create_index(op.f('ix_evidence_links_relationship_id'), 'evidence_links', ['relationship_id'], unique=False)
            op.create_index(op.f('ix_evidence_links_candidate_id'), 'evidence_links', ['candidate_id'], unique=False)
            op.create_index(op.f('ix_evidence_links_document_chunk_id'), 'evidence_links', ['document_chunk_id'], unique=False)
    except ProgrammingError as e:
        if "already exists" in str(e):
            pass
        else:
            raise


def downgrade() -> None:
    op.drop_index(op.f('ix_evidence_links_document_chunk_id'), table_name='evidence_links')
    op.drop_index(op.f('ix_evidence_links_candidate_id'), table_name='evidence_links')
    op.drop_index(op.f('ix_evidence_links_relationship_id'), table_name='evidence_links')
    op.drop_table('evidence_links')
