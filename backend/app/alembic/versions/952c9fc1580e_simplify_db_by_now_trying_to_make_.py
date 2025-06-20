"""Simplify db by now, trying to make fronted-backend work

Revision ID: 952c9fc1580e
Revises: d856c0bad7f2
Create Date: 2025-01-30 10:37:04.709132

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '952c9fc1580e'
down_revision = 'd856c0bad7f2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('order', 'out_document')
    op.drop_column('order', 'out_document_name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('out_document_name', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('order', sa.Column('out_document', postgresql.BYTEA(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
