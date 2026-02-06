"""Merge two heads

Revision ID: e6c409682bb7
Revises: 1c1ed72dfd2c, 311e16a20ad4
Create Date: 2026-02-06 11:32:30.253458

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6c409682bb7'
down_revision: Union[str, Sequence[str], None] = ('1c1ed72dfd2c', '311e16a20ad4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
