from alembic import op
import sqlalchemy as sa
from sqlalchemy.exc import ProgrammingError
from typing import Sequence, Union
import sqlalchemy as sa
from typing import Sequence, Union

revision = 'c3a1d7e8f204'
down_revision = '1fb69dab13ab'
branch_labels = None
def upgrade():
    try:
        with op.get_bind().begin_nested():
            op.add_column('ingestion_jobs', sa.Column('chunk_count', sa.Integer(), nullable=True))
    except ProgrammingError as e:
        if "already exists" in str(e):
            pass
        else:
            raise

def downgrade():
    op.drop_column('ingestion_jobs', 'chunk_count')
