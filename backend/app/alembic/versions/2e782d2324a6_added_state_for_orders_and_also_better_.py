"""Added state for orders, and also better dates tracking

Revision ID: 2e782d2324a6
Revises: b323359e7c19
Create Date: 2025-04-27 19:43:48.693268

"""

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "2e782d2324a6"
down_revision = "b323359e7c19"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Create the enum type first
    order_state_enum = postgresql.ENUM(
        "PENDING", "INTEGRATED", "ERROR", name="order_state_enum"
    )
    order_state_enum.create(op.get_bind())

    # Add the column as nullable first
    op.add_column("order", sa.Column("state", order_state_enum, nullable=True))

    # Update existing rows to have a default value
    op.execute("UPDATE \"order\" SET state = 'PENDING' WHERE state IS NULL")

    # Now make the column non-nullable
    op.alter_column("order", "state", nullable=False)

    # Add the other columns
    op.add_column("order", sa.Column("approved_at", sa.DateTime(), nullable=True))
    op.add_column(
        "order", sa.Column("erp_interaction_at", sa.DateTime(), nullable=True)
    )
    op.drop_column("order", "is_approved")
    op.drop_column("order", "date_approved")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "order",
        sa.Column(
            "date_approved", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
    )
    op.add_column(
        "order",
        sa.Column("is_approved", sa.BOOLEAN(), autoincrement=False, nullable=True),
    )
    op.drop_column("order", "erp_interaction_at")
    op.drop_column("order", "approved_at")
    op.drop_column("order", "state")

    # Drop the enum type
    postgresql.ENUM(name="order_state_enum").drop(op.get_bind())
    # ### end Alembic commands ###
