"""create oauth2 table

Revision ID: a90d927ffda8
Revises: 61ac0b69b150
Create Date: 2024-10-09 17:05:31.522984

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a90d927ffda8'
down_revision: Union[str, None] = '61ac0b69b150'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('oauth2',
                    sa.Column('id', sa.Integer(), primary_key=True),
                    sa.Column('hostname', sa.String(), nullable=False),
                    sa.Column('access_token', sa.String(), nullable=False),
                    sa.Column('refresh_token', sa.String(), nullable=False),
                    sa.Column('expires_in', sa.Integer(), nullable=False),
                    sa.Column('issued_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
                    )


def downgrade() -> None:
    op.drop_table('oauth2')
