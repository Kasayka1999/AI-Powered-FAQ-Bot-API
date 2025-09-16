"""add document_chunks metadata fields

Revision ID: 3a3d6cb391ad
Revises: 828f3e60efc5
Create Date: 2025-09-16 15:22:22.220759

"""
from typing import Sequence, Union

import sqlmodel
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '3a3d6cb391ad'
down_revision: Union[str, Sequence[str], None] = '828f3e60efc5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "document_chunks",
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
    )
    op.add_column(
        "document_chunks",
        sa.Column("chunk_index", sa.Integer(), nullable=True),
    )
    op.add_column(
        "document_chunks",
        sa.Column("content_length", sa.Integer(), nullable=True),
    )
    op.add_column(
        "document_chunks",
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
    )


def downgrade():
    op.drop_column("document_chunks", "created_at")
    op.drop_column("document_chunks", "content_length")
    op.drop_column("document_chunks", "chunk_index")
    op.drop_column("document_chunks", "metadata")
