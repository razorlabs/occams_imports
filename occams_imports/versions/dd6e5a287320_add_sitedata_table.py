"""Add sitedata table.

Revision ID: dd6e5a287320
Revises: 963a751621f5
Create Date: 2016-10-06 16:39:21.370434

"""

# revision identifiers, used by Alembic.
revision = 'dd6e5a287320'
down_revision = '963a751621f5'
branch_labels = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy import sql
from sqlalchemy.dialects.postgresql import JSONB


def upgrade():
    """Create table to store site data."""
    op.create_table(
        'sitedata',
        sa.Column(
            'id',
            sa.Integer,
            primary_key=True,
            autoincrement=True,
            nullable=False),
        sa.Column('study_id', sa.Integer, nullable=False),
        sa.Column('schema_id', sa.Integer, nullable=False),
        sa.Column('data', JSONB, nullable=False),
        sa.Column('create_user_id', sa.Integer, nullable=False),
        sa.Column('create_date',
                  sa.DateTime,
                  nullable=False,
                  server_default=sql.func.now()),
        sa.Column('modify_user_id', sa.Integer, nullable=False),
        sa.Column('modify_date',
                  sa.DateTime,
                  nullable=False,
                  server_default=sql.func.now()),
        sa.Index('ix_sitedata_create_user_id', 'create_user_id'),
        sa.Index('ix_sitedata_modify_user_id', 'modify_user_id'),
        # Both main/audit tables keep the same check constraint names
        sa.CheckConstraint('create_date <= modify_date',
                           name='ck_sitedata_valid_timeline'),
        schema='imports'
    )

    op.create_foreign_key(
        'fk_sitedata_create_user_id', 'sitedata',
        'user', ['create_user_id'], ['id'], ondelete='RESTRICT',
        source_schema='imports')
    op.create_foreign_key(
        'fk_sitedata_modify_user_id', 'sitedata',
        'user', ['modify_user_id'], ['id'], ondelete='RESTRICT',
        source_schema='imports')
    op.create_foreign_key(
        'fk_sitedata_study_id', 'sitedata',
        'study', ['study_id'], ['id'], ondelete='CASCADE',
        source_schema='imports')
    op.create_foreign_key(
        'fk_sitedata_schema_id', 'sitedata',
        'schema', ['schema_id'], ['id'], ondelete='CASCADE',
        source_schema='imports')


def downgrade():
    """Drop table on downgrade."""
    op.drop_table('sitedata', schema='imports')
