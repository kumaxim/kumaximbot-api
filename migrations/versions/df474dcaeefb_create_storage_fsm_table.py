"""aiogram fsm

Revision ID: df474dcaeefb
Revises: 864f1771ab8f
Create Date: 2024-10-06 18:28:25.031605

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df474dcaeefb'
down_revision: Union[str, None] = '864f1771ab7o'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('storage_fsm',
                    sa.Column('bot_id', sa.Integer(), nullable=False),
                    sa.Column('chat_id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('thread_id', sa.Integer(), nullable=True),
                    sa.Column('business_connection_id', sa.String(), nullable=True),
                    sa.Column('destiny', sa.String()),
                    sa.Column('state', sa.Text(), nullable=True),
                    sa.Column('data', sa.Text(), nullable=True),
                    sa.PrimaryKeyConstraint('chat_id', 'user_id'),
                    )


def downgrade() -> None:
    op.drop_table('storage_fsm')
