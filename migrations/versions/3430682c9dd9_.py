"""empty message

Revision ID: 3430682c9dd9
Revises: 8170353d98a1
Create Date: 2020-08-24 13:55:57.791653

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3430682c9dd9'
down_revision = '8170353d98a1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('genres', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'genres')
    # ### end Alembic commands ###
