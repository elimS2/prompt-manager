"""Add is_public to prompts (SQLite-safe)

Revision ID: d6108f958397
Revises: c6fd79d6affc
Create Date: 2025-08-26 00:19:30.653175
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd6108f958397'
down_revision = 'c6fd79d6affc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Only add column + index; avoid ALTER COLUMN (SQLite incompatible)
    op.add_column('prompts', sa.Column('is_public', sa.Boolean(), nullable=False, server_default=sa.text('0')))
    op.create_index('ix_prompts_is_public', 'prompts', ['is_public'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_prompts_is_public', table_name='prompts')
    op.drop_column('prompts', 'is_public')


