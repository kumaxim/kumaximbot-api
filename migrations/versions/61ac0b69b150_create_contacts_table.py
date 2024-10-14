"""create contacts table

Revision ID: 61ac0b69b150
Revises: df474dcaeefb
Create Date: 2024-10-08 17:07:20.389202

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '61ac0b69b150'
down_revision: Union[str, None] = '864f1771ab7o'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('contacts',
                    sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
                    sa.Column('first_name', sa.String(), nullable=False),
                    sa.Column('last_name', sa.String(), nullable=False),
                    sa.Column('phone_number', sa.String(), nullable=False),
                    sa.Column('resume_url', sa.String(), nullable=False),
                    sa.Column('email', sa.String(), nullable=False),
                    )


def downgrade() -> None:
    op.drop_table('contacts')
