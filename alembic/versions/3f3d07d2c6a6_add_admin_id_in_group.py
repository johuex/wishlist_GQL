"""add admin_id in Group

Revision ID: 3f3d07d2c6a6
Revises: 5bc53810cf97
Create Date: 2021-04-27 16:13:27.191666

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f3d07d2c6a6'
down_revision = '5bc53810cf97'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('group', sa.Column('admin_id', sa.Integer, sa.ForeignKey('users.id')))


def downgrade():
    op.drop_column('group', 'admin_id')
