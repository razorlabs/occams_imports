"""Change logic field from JSON to JSONB

Revision ID: 963a751621f5
Revises: f8b70e3f7a59
Create Date: 2016-10-06 13:57:41.446720

"""

# revision identifiers, used by Alembic.
revision = '963a751621f5'
down_revision = 'f8b70e3f7a59'
branch_labels = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.postgresql import JSONB


def upgrade():
    op.alter_column('mapping', 'logic', schema='imports', type_=JSONB)


def downgrade():
    op.alter_column('mapping', 'logic', schema='imports', type_=JSON)
