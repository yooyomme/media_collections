"""seed_categories_data

Revision ID: 0d70b6ab6f60
Revises: 3fe60b0366db
Create Date: 2026-03-11 20:53:03.436493

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d70b6ab6f60'
down_revision: Union[str, Sequence[str], None] = '3fe60b0366db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.execute(
        """
        INSERT IGNORE INTO categories (id, slug, title)
        VALUES 
            (1, 'movie', 'Фильм'),
            (2, 'tv', 'Сериал'),
            (3, 'anime', 'Аниме');
        """
    )

def downgrade():
    op.execute("DELETE FROM categories WHERE id IN (1, 2, 3);")
