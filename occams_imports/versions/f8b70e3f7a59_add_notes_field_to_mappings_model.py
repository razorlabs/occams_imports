"""Add notes field to mappings model

Revision ID: f8b70e3f7a59
Revises: None
Create Date: 2016-09-19 11:21:50.162774

"""

# revision identifiers, used by Alembic.
revision = 'f8b70e3f7a59'
down_revision = None
branch_labels = ('imports',)

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('mapping', sa.Column('notes', sa.UnicodeText()), schema='imports')


def downgrade():
    pass
