"""change_content_registered_to_text

Revision ID: 5943ca4d800a
Revises: e5a8dd604b44
Create Date: 2025-04-22 13:12:45.006807

"""

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision = "5943ca4d800a"
down_revision = "e5a8dd604b44"
branch_labels = None
depends_on = None


def upgrade():
    # Change content_registered from VARCHAR(255) to TEXT
    op.alter_column(
        "order",
        "content_registered",
        existing_type=sa.String(length=255),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade():
    # Change content_registered back to VARCHAR(255)
    op.alter_column(
        "order",
        "content_registered",
        existing_type=sa.Text(),
        type_=sa.String(length=255),
        existing_nullable=True,
    )
