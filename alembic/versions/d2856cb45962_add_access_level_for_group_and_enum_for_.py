"""add access_level for group and enum for group_access

Revision ID: d2856cb45962
Revises: 3f3d07d2c6a6
Create Date: 2021-04-30 13:29:10.215569

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2856cb45962'
down_revision = '3f3d07d2c6a6'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE TYPE group_access AS ENUM ('OPEN', 'CLOSE');")
    op.execute('ALTER TABLE "group" ALTER COLUMN access_level TYPE group_access USING access_level::group_access')


def downgrade():
    pass
