"""Also done the update for emails

Revision ID: fa4198655639
Revises: 2e782d2324a6
Create Date: 2025-04-27 19:53:21.734575

"""

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "fa4198655639"
down_revision = "2e782d2324a6"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Create the enum type first
    email_state_enum = postgresql.ENUM("PROCESSED", "ERROR", name="email_state_enum")
    email_state_enum.create(op.get_bind())

    # Add the column as nullable first
    op.add_column("email", sa.Column("state", email_state_enum, nullable=True))

    # Update existing rows to have a default value based on is_processed
    op.execute("UPDATE email SET state = 'PROCESSED' WHERE is_processed = true")
    op.execute("UPDATE email SET state = 'ERROR' WHERE is_processed = false")

    # Now make the column non-nullable
    op.alter_column("email", "state", nullable=False)

    # Drop the old column
    op.drop_column("email", "is_processed")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Add the old column back
    op.add_column(
        "email",
        sa.Column("is_processed", sa.BOOLEAN(), autoincrement=False, nullable=True),
    )

    # Update the old column based on the state
    op.execute("UPDATE email SET is_processed = true WHERE state = 'PROCESSED'")
    op.execute("UPDATE email SET is_processed = false WHERE state = 'ERROR'")

    # Make the old column non-nullable
    op.alter_column("email", "is_processed", nullable=False)

    # Drop the new column
    op.drop_column("email", "state")

    # Drop the enum type
    postgresql.ENUM(name="email_state_enum").drop(op.get_bind())
    # ### end Alembic commands ###
