"""Add user status fields and email_allowlist table

Revision ID: 7900128ca2d6
Revises: 5e7f403399eb
Create Date: 2025-08-10 23:05:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7900128ca2d6'
down_revision = '5e7f403399eb'
branch_labels = None
depends_on = None


def upgrade():
    # users table: add status, approved_at, approved_by_user_id
    op.add_column('users', sa.Column('status', sa.String(length=20), nullable=False, server_default='active'))
    op.add_column('users', sa.Column('approved_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('approved_by_user_id', sa.Integer(), nullable=True))
    op.create_index('ix_users_status', 'users', ['status'])

    # email_allowlist table
    op.create_table(
        'email_allowlist',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('default_role', sa.String(length=50), nullable=False, server_default='user'),
        sa.Column('note', sa.String(length=255), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='uq_email_allowlist_email')
    )


def downgrade():
    # email_allowlist table
    op.drop_table('email_allowlist')

    # users table
    op.drop_index('ix_users_status', table_name='users')
    op.drop_column('users', 'approved_by_user_id')
    op.drop_column('users', 'approved_at')
    op.drop_column('users', 'status')


