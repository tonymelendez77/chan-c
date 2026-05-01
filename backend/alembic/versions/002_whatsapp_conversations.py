"""add whatsapp conversations table

Revision ID: 002
Revises: 001
Create Date: 2026-04-30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "whatsapp_conversations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("phone", sa.String(50), unique=True, nullable=False),
        sa.Column("role", sa.String(20), nullable=True),
        sa.Column("state", sa.String(50), nullable=False, server_default="idle"),
        sa.Column("data", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("worker_id", UUID(as_uuid=True), sa.ForeignKey("workers.id"), nullable=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=True),
        sa.Column("needs_human", sa.Boolean(), default=False, nullable=False, server_default=sa.text("false")),
        sa.Column("last_message_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_whatsapp_conversations_phone", "whatsapp_conversations", ["phone"], unique=True)
    op.create_index("ix_whatsapp_conversations_worker_id", "whatsapp_conversations", ["worker_id"])
    op.create_index("ix_whatsapp_conversations_company_id", "whatsapp_conversations", ["company_id"])


def downgrade() -> None:
    op.drop_index("ix_whatsapp_conversations_company_id", "whatsapp_conversations")
    op.drop_index("ix_whatsapp_conversations_worker_id", "whatsapp_conversations")
    op.drop_index("ix_whatsapp_conversations_phone", "whatsapp_conversations")
    op.drop_table("whatsapp_conversations")
