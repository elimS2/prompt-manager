"""Add user_id to prompts (SQLite-safe)

Revision ID: 8313c3d6680e
Revises: 7900128ca2d6
Create Date: 2025-08-25
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8313c3d6680e'
down_revision = '7900128ca2d6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # SQLite-safe add column and index
    op.add_column('prompts', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_index('ix_prompts_user_id', 'prompts', ['user_id'], unique=False)
    # Create FK if supported; SQLite will accept it in newer versions
    try:
        op.create_foreign_key(
            'fk_prompts_user_id_users', 'prompts', 'users', ['user_id'], ['id'], ondelete='SET NULL'
        )
    except Exception:
        # Ignore if dialect/SQLite version doesn't support creating FK here
        pass


def downgrade() -> None:
    try:
        op.drop_constraint('fk_prompts_user_id_users', 'prompts', type_='foreignkey')
    except Exception:
        pass
    op.drop_index('ix_prompts_user_id', table_name='prompts')
    op.drop_column('prompts', 'user_id')


