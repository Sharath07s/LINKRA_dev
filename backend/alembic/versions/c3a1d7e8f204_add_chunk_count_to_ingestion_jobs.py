from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

revision = 'c3a1d7e8f204'
down_revision = '1fb69dab13ab'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('ingestion_jobs', sa.Column('chunk_count', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('ingestion_jobs', 'chunk_count')
