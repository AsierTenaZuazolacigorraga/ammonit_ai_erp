"""Added OEE data there

Revision ID: 189477a91917
Revises: f3fdf8cfca72
Create Date: 2024-12-29 11:55:44.113696

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '189477a91917'
down_revision = 'f3fdf8cfca72'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('machine', sa.Column('oee', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True))
    op.add_column('machine', sa.Column('oee_availability', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True))
    op.add_column('machine', sa.Column('oee_performance', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True))
    op.add_column('machine', sa.Column('oee_quality', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('machine', 'oee_quality')
    op.drop_column('machine', 'oee_performance')
    op.drop_column('machine', 'oee_availability')
    op.drop_column('machine', 'oee')
    # ### end Alembic commands ###
