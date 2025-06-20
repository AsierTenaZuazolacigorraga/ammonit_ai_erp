"""Added structure description

Revision ID: 86440f30897c
Revises: ef494c5350c1
Create Date: 2025-05-24 11:22:31.041891

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '86440f30897c'
down_revision = 'ef494c5350c1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('client', sa.Column('structure_descriptions', sa.JSON(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('client', 'structure_descriptions')
    # ### end Alembic commands ###
