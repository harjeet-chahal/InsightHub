"""add_source_status

Revision ID: 002_add_source_status
Revises: 001_init_schema
Create Date: 2024-03-25 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_add_source_status'
down_revision: Union[str, None] = '001_init_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('sources', sa.Column('status', sa.String(), server_default='pending', nullable=False))
    op.add_column('sources', sa.Column('error_message', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('sources', 'error_message')
    op.drop_column('sources', 'status')
