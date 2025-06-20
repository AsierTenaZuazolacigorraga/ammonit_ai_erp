"""Add utc time management

Revision ID: 7e120fe92024
Revises: 74704f7e7334
Create Date: 2025-01-30 13:44:38.128238

"""

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "7e120fe92024"
down_revision = "74704f7e7334"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "order",
        sa.Column(
            "date_locale", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
    )
    op.add_column(
        "order",
        sa.Column(
            "date_utc", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
    )
    op.drop_column("order", "date")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "order",
        sa.Column("date", postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    )
    op.drop_column("order", "date_utc")
    op.drop_column("order", "date_locale")
    # ### end Alembic commands ###
