"""add feature control tables

Revision ID: 0004_feature_control
Revises: 0003_add_wallet_notice_timestamp
Create Date: 2026-01-08

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '0004_feature_control'
down_revision = '0003_add_wallet_notice_timestamp'
branch_labels = None
depends_on = None


def upgrade():
    # 建立群組功能設定表
    op.create_table(
        'group_feature_setting',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('group_id', sa.String(length=100), nullable=False),
        sa.Column('token', sa.String(length=100), nullable=False),
        sa.Column('features', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_group_feature_setting_group_id', 'group_feature_setting', ['group_id'], unique=True)
    op.create_index('ix_group_feature_setting_token', 'group_feature_setting', ['token'], unique=True)
    
    # 建立指令配置表
    op.create_table(
        'command_config',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('command_key', sa.String(length=50), nullable=False),
        sa.Column('command_zh', sa.String(length=100), nullable=False),
        sa.Column('command_en', sa.String(length=100), nullable=True),
        sa.Column('feature_category', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('is_admin_only', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_command_config_command_key', 'command_config', ['command_key'], unique=True)
    
    # 建立功能使用記錄表
    op.create_table(
        'feature_usage_log',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('group_id', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.String(length=100), nullable=False),
        sa.Column('feature_key', sa.String(length=50), nullable=False),
        sa.Column('command_used', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_feature_usage_log_group_id', 'feature_usage_log', ['group_id'])
    op.create_index('ix_feature_usage_log_user_id', 'feature_usage_log', ['user_id'])
    op.create_index('ix_feature_usage_log_created_at', 'feature_usage_log', ['created_at'])


def downgrade():
    op.drop_table('feature_usage_log')
    op.drop_table('command_config')
    op.drop_table('group_feature_setting')
