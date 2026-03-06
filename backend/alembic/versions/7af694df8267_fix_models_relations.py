"""Fix models relations

Revision ID: 7af694df8267
Revises: e6c409682bb7
Create Date: 2026-02-06 11:36:07.279247

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '7af694df8267'
down_revision: Union[str, Sequence[str], None] = 'e6c409682bb7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('media_items_collections_ibfk_1', 'media_items_collections', type_='foreignkey')

    op.alter_column('media_items_collections', 'collection_id',
               existing_type=mysql.INTEGER(),
               type_=sa.CHAR(length=36),
               existing_nullable=False)

    op.create_foreign_key(
        'media_items_collections_ibfk_1',
        'media_items_collections',
        'collections',
        ['collection_id'],
        ['id'],
        ondelete='CASCADE'
    )

def downgrade() -> None:
    op.drop_constraint('media_items_collections_ibfk_1', 'media_items_collections', type_='foreignkey')

    op.alter_column('media_items_collections', 'collection_id',
               existing_type=sa.CHAR(length=36),
               type_=mysql.INTEGER(),
               existing_nullable=False)

    op.create_foreign_key(
        'media_items_collections_ibfk_1',
        'media_items_collections',
        'collections',
        ['collection_id'],
        ['id'],
        ondelete='CASCADE'
    )