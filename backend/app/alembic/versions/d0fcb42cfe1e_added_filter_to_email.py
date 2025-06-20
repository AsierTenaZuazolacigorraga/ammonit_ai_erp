"""Added filter to email

Revision ID: d0fcb42cfe1e
Revises: e2de961dd6d5
Create Date: 2025-05-18 19:12:44.959584

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'd0fcb42cfe1e'
down_revision = 'e2de961dd6d5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('email', sa.Column('filter', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('email', 'filter')
    # ### end Alembic commands ###
