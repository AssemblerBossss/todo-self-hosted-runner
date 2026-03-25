"""add details_hash to todos

Revision ID: f1a2b3c4d5e6
Revises: 0d80d1ceace1
Create Date: 2026-03-25 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, None] = '0d80d1ceace1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE todos ADD COLUMN IF NOT EXISTS details_hash VARCHAR")


def downgrade() -> None:
    op.execute("ALTER TABLE todos DROP COLUMN IF EXISTS details_hash")
