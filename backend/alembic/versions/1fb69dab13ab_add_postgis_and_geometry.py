"""add_postgis_and_geometry

Revision ID: 1fb69dab13ab
Revises: 2044efa5955a
Create Date: 2026-09-08 07:00:02.564563

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1fb69dab13ab'
down_revision: Union[str, Sequence[str], None] = '2044efa5955a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Enable PostGIS
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    
    # 2. Add location columns
    import geoalchemy2
    op.add_column('crimes', sa.Column('location', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326), nullable=True))
    op.add_column('police_stations', sa.Column('location', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326), nullable=True))
    
    # 3. Backfill data
    op.execute("""
        UPDATE crimes 
        SET location = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326) 
        WHERE longitude IS NOT NULL AND latitude IS NOT NULL 
          AND latitude BETWEEN -90 AND 90 
          AND longitude BETWEEN -180 AND 180;
    """)
    op.execute("""
        UPDATE police_stations 
        SET location = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326) 
        WHERE longitude IS NOT NULL AND latitude IS NOT NULL
          AND latitude BETWEEN -90 AND 90 
          AND longitude BETWEEN -180 AND 180;
    """)
    
    # 4. GiST Indexes
    # 4. GiST Indexes are automatically created by GeoAlchemy2
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS idx_police_stations_location;")
    op.execute("DROP INDEX IF EXISTS idx_crimes_location;")
    op.drop_column('police_stations', 'location')
    op.drop_column('crimes', 'location')
    # Leaving PostGIS extension as it's safe to keep
