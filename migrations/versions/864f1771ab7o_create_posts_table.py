"""Init

Revision ID: 864f1771ab8f
Revises: 
Create Date: 2024-08-27 21:43:44.635673

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '864f1771ab7o'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('posts',
                    sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
                    sa.Column('command', sa.String(), unique=True, nullable=False),
                    sa.Column('text', sa.Text(), nullable=False),

                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('posts')
    # ### end Alembic commands ###
