"""Update clients model

Revision ID: fb9ed1210058
Revises: 29cd8f456e1e
Create Date: 2025-05-22 17:34:12.736140

"""

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision = "fb9ed1210058"
down_revision = "29cd8f456e1e"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("client", sa.Column("base_document", sa.LargeBinary(), nullable=True))
    op.add_column(
        "client",
        sa.Column(
            "base_document_name",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=True,
        ),
    )
    op.add_column(
        "client",
        sa.Column(
            "base_document_markdown", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
    )
    op.add_column("client", sa.Column("structure", sa.JSON(), nullable=True))
    op.add_column(
        "client",
        sa.Column("additional_info", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.alter_column(
        "client", "content_processed", existing_type=sa.VARCHAR(), nullable=True
    )
    op.drop_column("client", "base_markdown")
    # Fill base_document for existing rows with empty bytes
    op.execute("UPDATE client SET base_document = '' WHERE base_document IS NULL")
    # Now alter the column to be NOT NULL
    op.alter_column("client", "base_document", nullable=False)
    # Fill structure for existing rows with empty JSON object
    op.execute("UPDATE client SET structure = '{}' WHERE structure IS NULL")
    # Now alter the column to be NOT NULL
    op.alter_column("client", "structure", nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "client",
        sa.Column("base_markdown", sa.VARCHAR(), autoincrement=False, nullable=False),
    )
    op.alter_column(
        "client", "content_processed", existing_type=sa.VARCHAR(), nullable=False
    )
    op.drop_column("client", "additional_info")
    op.drop_column("client", "structure")
    op.drop_column("client", "base_document_markdown")
    op.drop_column("client", "base_document_name")
    op.drop_column("client", "base_document")
    # ### end Alembic commands ###
