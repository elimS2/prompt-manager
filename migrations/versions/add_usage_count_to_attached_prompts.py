"""add usage count to attached prompts

Revision ID: add_usage_count_to_attached_prompts
Revises: add_attached_prompts_table
Create Date: 2025-08-04 02:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_usage_count_to_attached_prompts'
down_revision = 'add_attached_prompts_table'
branch_labels = None
depends_on = None


def upgrade():
    """Add usage_count column to attached_prompts table."""
    op.add_column('attached_prompts', sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'))
    op.create_index(op.f('ix_attached_prompts_usage_count'), 'attached_prompts', ['usage_count'], unique=False)


def downgrade():
    """Remove usage_count column from attached_prompts table."""
    op.drop_index(op.f('ix_attached_prompts_usage_count'), table_name='attached_prompts')
    op.drop_column('attached_prompts', 'usage_count') 