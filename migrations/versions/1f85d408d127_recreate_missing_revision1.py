"""Recreate missing revision1

Revision ID: 1f85d408d127
Revises: d290ac8069ad
Create Date: 2025-07-21 12:03:03.360862

"""
from typing import Sequence, Union

import sqlmodel
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f85d408d127'
down_revision: Union[str, Sequence[str], None] = 'd290ac8069ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
