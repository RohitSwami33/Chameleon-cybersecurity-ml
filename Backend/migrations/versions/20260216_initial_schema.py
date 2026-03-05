"""Initial schema with tenants, honeypot_logs, and reputation_scores

Revision ID: 001
Revises: 
Create Date: 2024-01-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial database schema."""
    
    # Create tenants table
    op.create_table(
        'tenants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('api_key', sa.String(64), unique=True, nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('credit_balance', sa.Integer, nullable=False, server_default='1000'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create indexes for tenants
    op.create_index('ix_tenants_id', 'tenants', ['id'])
    op.create_index('ix_tenants_api_key', 'tenants', ['api_key'])
    op.create_index('ix_tenants_email', 'tenants', ['email'])
    
    # Create honeypot_logs table
    op.create_table(
        'honeypot_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('attacker_ip', sa.String(45), nullable=False),
        sa.Column('command_entered', sa.Text, nullable=False),
        sa.Column('response_sent', sa.Text, nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
    )
    
    # Create indexes for honeypot_logs
    op.create_index('ix_honeypot_logs_id', 'honeypot_logs', ['id'])
    op.create_index('ix_honeypot_logs_tenant_id', 'honeypot_logs', ['tenant_id'])
    op.create_index('ix_honeypot_logs_attacker_ip', 'honeypot_logs', ['attacker_ip'])
    op.create_index('ix_honeypot_logs_timestamp', 'honeypot_logs', ['timestamp'])
    op.create_index('ix_honeypot_logs_tenant_timestamp', 'honeypot_logs', ['tenant_id', 'timestamp'])
    op.create_index('ix_honeypot_logs_ip_timestamp', 'honeypot_logs', ['attacker_ip', 'timestamp'])
    
    # Create reputation_scores table
    op.create_table(
        'reputation_scores',
        sa.Column('ip_address', sa.String(45), primary_key=True),
        sa.Column('reputation_score', sa.Integer, nullable=False, server_default='100'),
        sa.Column('behavior_hash', sa.String(64), nullable=True),
        sa.Column('merkle_root', sa.String(64), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('attack_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('attack_types', postgresql.JSONB, nullable=True),
    )


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('reputation_scores')
    op.drop_table('honeypot_logs')
    op.drop_table('tenants')