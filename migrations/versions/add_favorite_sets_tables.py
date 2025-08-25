"""add favorite sets tables

Revision ID: add_favorite_sets_tables
Revises: 5e7f403399eb_create_users_table_for_google_oauth
Create Date: 2025-08-17
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_favorite_sets_tables'
down_revision = '7900128ca2d6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'favorite_sets',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'name', name='uq_favorite_set_user_name')
    )
    op.create_index(op.f('ix_favorite_sets_user_id'), 'favorite_sets', ['user_id'], unique=False)

    op.create_table(
        'favorite_set_items',
        sa.Column('favorite_set_id', sa.Integer(), nullable=False),
        sa.Column('prompt_id', sa.Integer(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['favorite_set_id'], ['favorite_sets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['prompt_id'], ['prompts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('favorite_set_id', 'prompt_id', name='uq_favorite_item_unique_prompt')
    )
    op.create_index(op.f('ix_favorite_set_items_favorite_set_id'), 'favorite_set_items', ['favorite_set_id'], unique=False)
    op.create_index(op.f('ix_favorite_set_items_prompt_id'), 'favorite_set_items', ['prompt_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_favorite_set_items_prompt_id'), table_name='favorite_set_items')
    op.drop_index(op.f('ix_favorite_set_items_favorite_set_id'), table_name='favorite_set_items')
    op.drop_table('favorite_set_items')
    op.drop_index(op.f('ix_favorite_sets_user_id'), table_name='favorite_sets')
    op.drop_table('favorite_sets')


