"""Initial schema - all 16 tables

Revision ID: 001
Revises:
Create Date: 2026-04-04
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Enum types ---
    user_role = sa.Enum(
        "admin", "company", "worker", name="user_role", create_type=True
    )
    company_type = sa.Enum(
        "construction", "architecture", "property_management", "other",
        name="company_type", create_type=True,
    )
    subscription_plan = sa.Enum(
        "none", "basic", "pro", name="subscription_plan", create_type=True
    )
    language = sa.Enum(
        "spanish", "kiche", "mam", "other", name="language", create_type=True
    )
    profile_status = sa.Enum(
        "pending_review", "active", "suspended",
        name="profile_status", create_type=True,
    )
    trade = sa.Enum(
        "electrician", "plumber", "carpenter", "mason", "painter", "welder",
        "roofer", "general_labor", "security", "housemaid", "gardener", "other",
        name="trade", create_type=True,
    )
    skill_level = sa.Enum(
        "junior", "mid", "senior", name="skill_level", create_type=True
    )
    skill_level_required = sa.Enum(
        "junior", "mid", "senior", "any",
        name="skill_level_required", create_type=True,
    )
    reference_outcome = sa.Enum(
        "positive", "neutral", "negative",
        name="reference_outcome", create_type=True,
    )
    reference_call_status = sa.Enum(
        "pending", "completed", "no_answer", "failed",
        name="reference_call_status", create_type=True,
    )
    job_status = sa.Enum(
        "draft", "open", "matching", "filled", "completed", "cancelled",
        name="job_status", create_type=True,
    )
    match_status = sa.Enum(
        "pending_company", "pending_worker", "pending_ai_call",
        "call_in_progress", "pending_review", "pending_company_decision",
        "accepted", "rejected_company", "rejected_worker", "cancelled",
        name="match_status", create_type=True,
    )
    worker_reply = sa.Enum(
        "yes", "no", "contra", "problema", name="worker_reply", create_type=True
    )
    counteroffer_proposed_by = sa.Enum(
        "worker", "company", name="counteroffer_proposed_by", create_type=True
    )
    counteroffer_status = sa.Enum(
        "pending", "accepted", "rejected",
        name="counteroffer_status", create_type=True,
    )
    ai_call_type = sa.Enum(
        "intake", "reference_check", "job_offer", "counteroffer", "post_job_rating",
        name="ai_call_type", create_type=True,
    )
    ai_call_status = sa.Enum(
        "initiated", "in_progress", "completed", "failed", "no_answer",
        name="ai_call_status", create_type=True,
    )
    extraction_final_status = sa.Enum(
        "interested", "not_interested", "interested_with_conditions",
        name="extraction_final_status", create_type=True,
    )
    onboarding_call_type = sa.Enum(
        "intake", "reference_check", name="onboarding_call_type", create_type=True
    )
    sms_direction = sa.Enum(
        "inbound", "outbound", name="sms_direction", create_type=True
    )
    sms_status = sa.Enum(
        "sent", "delivered", "failed", "received",
        name="sms_status", create_type=True,
    )
    rated_by = sa.Enum("company", "worker", name="rated_by", create_type=True)
    payment_type = sa.Enum(
        "placement_fee", "subscription", name="payment_type", create_type=True
    )
    payment_status = sa.Enum(
        "pending", "invoiced", "paid", "overdue",
        name="payment_status", create_type=True,
    )

    # --- 1. users ---
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
    )
    op.create_index("ix_users_created_at", "users", ["created_at"])

    # --- 2. companies ---
    op.create_table(
        "companies",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("contact_name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(50), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("zone", sa.String(100), nullable=False),
        sa.Column("company_type", company_type, nullable=False),
        sa.Column("tax_id", sa.String(50), nullable=False),
        sa.Column("is_verified", sa.Boolean(), default=False, nullable=False),
        sa.Column("subscription_plan", subscription_plan, default="none", nullable=False),
        sa.Column("subscription_start", sa.Date(), nullable=True),
        sa.Column("subscription_end", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_companies_user_id", "companies", ["user_id"])
    op.create_index("ix_companies_created_at", "companies", ["created_at"])

    # --- 3. workers ---
    op.create_table(
        "workers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(50), unique=True, nullable=False),
        sa.Column("dpi", sa.String(50), nullable=True),
        sa.Column("zone", sa.String(100), nullable=False),
        sa.Column("language", language, default="spanish", nullable=False),
        sa.Column("is_available", sa.Boolean(), default=True, nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True, nullable=False),
        sa.Column("is_vetted", sa.Boolean(), default=False, nullable=False),
        sa.Column("vetting_date", sa.Date(), nullable=True),
        sa.Column("vetted_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("rating_avg", sa.Numeric(3, 2), default=0, nullable=False),
        sa.Column("total_jobs", sa.Integer(), default=0, nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_workers_phone", "workers", ["phone"])
    op.create_index("ix_workers_vetted_by", "workers", ["vetted_by"])
    op.create_index("ix_workers_created_at", "workers", ["created_at"])

    # --- 4. worker_profiles ---
    op.create_table(
        "worker_profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("worker_id", UUID(as_uuid=True), sa.ForeignKey("workers.id"), unique=True, nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("initial_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("profile_status", profile_status, default="pending_review", nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("profile_url", sa.String(500), nullable=True),
        sa.Column("total_earnings", sa.Numeric(12, 2), default=0, nullable=False),
        sa.Column("response_rate", sa.Numeric(5, 2), default=0, nullable=False),
        sa.Column("completion_rate", sa.Numeric(5, 2), default=0, nullable=False),
    )
    op.create_index("ix_worker_profiles_worker_id", "worker_profiles", ["worker_id"])

    # --- 5. worker_trades ---
    op.create_table(
        "worker_trades",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("worker_id", UUID(as_uuid=True), sa.ForeignKey("workers.id"), nullable=False),
        sa.Column("trade", trade, nullable=False),
        sa.Column("skill_level", skill_level, nullable=False),
        sa.Column("years_experience", sa.Integer(), nullable=False),
        sa.Column("can_cover", ARRAY(sa.String()), nullable=True),
        sa.Column("cannot_cover", ARRAY(sa.String()), nullable=True),
        sa.Column("verified_by_admin", sa.Boolean(), default=False, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_worker_trades_worker_id", "worker_trades", ["worker_id"])

    # --- 6. worker_references ---
    op.create_table(
        "worker_references",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("worker_id", UUID(as_uuid=True), sa.ForeignKey("workers.id"), nullable=False),
        sa.Column("reference_name", sa.String(255), nullable=False),
        sa.Column("reference_phone", sa.String(50), nullable=False),
        sa.Column("relationship", sa.String(100), nullable=False),
        sa.Column("call_date", sa.Date(), nullable=True),
        sa.Column("outcome", reference_outcome, nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("checked_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("ix_worker_references_worker_id", "worker_references", ["worker_id"])
    op.create_index("ix_worker_references_checked_by", "worker_references", ["checked_by"])

    # --- 7. reference_calls ---
    op.create_table(
        "reference_calls",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("worker_id", UUID(as_uuid=True), sa.ForeignKey("workers.id"), nullable=False),
        sa.Column("reference_name", sa.String(255), nullable=False),
        sa.Column("reference_phone", sa.String(50), nullable=False),
        sa.Column("call_status", reference_call_status, nullable=False),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("outcome", reference_outcome, nullable=True),
        sa.Column("confidence_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("ai_summary", sa.Text(), nullable=True),
        sa.Column("called_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_reference_calls_worker_id", "reference_calls", ["worker_id"])

    # --- 8. jobs ---
    op.create_table(
        "jobs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("trade_required", trade, nullable=False),
        sa.Column("skill_level_required", skill_level_required, nullable=False),
        sa.Column("zone", sa.String(100), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("daily_rate", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(10), default="GTQ", nullable=False),
        sa.Column("headcount", sa.Integer(), default=1, nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("special_requirements", sa.Text(), nullable=True),
        sa.Column("status", job_status, nullable=False),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_jobs_company_id", "jobs", ["company_id"])
    op.create_index("ix_jobs_status", "jobs", ["status"])
    op.create_index("ix_jobs_created_by", "jobs", ["created_by"])
    op.create_index("ix_jobs_created_at", "jobs", ["created_at"])

    # --- 9. matches ---
    op.create_table(
        "matches",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("job_id", UUID(as_uuid=True), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("worker_id", UUID(as_uuid=True), sa.ForeignKey("workers.id"), nullable=False),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", match_status, nullable=False),
        sa.Column("offered_rate", sa.Numeric(10, 2), nullable=False),
        sa.Column("final_rate", sa.Numeric(10, 2), nullable=True),
        sa.Column("company_notified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("worker_sms_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("worker_replied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("worker_reply", worker_reply, nullable=True),
        sa.Column("company_decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_matches_job_id", "matches", ["job_id"])
    op.create_index("ix_matches_worker_id", "matches", ["worker_id"])
    op.create_index("ix_matches_created_by", "matches", ["created_by"])
    op.create_index("ix_matches_status", "matches", ["status"])
    op.create_index("ix_matches_created_at", "matches", ["created_at"])

    # --- 10. counteroffers ---
    op.create_table(
        "counteroffers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("match_id", UUID(as_uuid=True), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("proposed_by", counteroffer_proposed_by, nullable=False),
        sa.Column("original_rate", sa.Numeric(10, 2), nullable=False),
        sa.Column("proposed_rate", sa.Numeric(10, 2), nullable=True),
        sa.Column("original_start", sa.Date(), nullable=False),
        sa.Column("proposed_start", sa.Date(), nullable=True),
        sa.Column("original_end", sa.Date(), nullable=False),
        sa.Column("proposed_end", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", counteroffer_status, nullable=False),
        sa.Column("responded_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_counteroffers_match_id", "counteroffers", ["match_id"])
    op.create_index("ix_counteroffers_responded_by", "counteroffers", ["responded_by"])

    # --- 11. ai_calls ---
    op.create_table(
        "ai_calls",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("match_id", UUID(as_uuid=True), sa.ForeignKey("matches.id"), nullable=True),
        sa.Column("worker_id", UUID(as_uuid=True), sa.ForeignKey("workers.id"), nullable=False),
        sa.Column("call_type", ai_call_type, nullable=False),
        sa.Column("vapi_call_id", sa.String(255), nullable=True),
        sa.Column("status", ai_call_status, nullable=False),
        sa.Column("language_detected", language, nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("recording_url", sa.String(500), nullable=True),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ai_calls_match_id", "ai_calls", ["match_id"])
    op.create_index("ix_ai_calls_worker_id", "ai_calls", ["worker_id"])
    op.create_index("ix_ai_calls_status", "ai_calls", ["status"])

    # --- 12. ai_extractions ---
    op.create_table(
        "ai_extractions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("call_id", UUID(as_uuid=True), sa.ForeignKey("ai_calls.id"), nullable=False),
        sa.Column("can_cover", ARRAY(sa.String()), nullable=True),
        sa.Column("cannot_cover", ARRAY(sa.String()), nullable=True),
        sa.Column("counteroffer_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("counteroffer_dates", sa.String(255), nullable=True),
        sa.Column("counteroffer_notes", sa.Text(), nullable=True),
        sa.Column("availability_notes", sa.Text(), nullable=True),
        sa.Column("final_status", extraction_final_status, nullable=True),
        sa.Column("confidence_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("requires_admin_review", sa.Boolean(), default=False, nullable=False),
        sa.Column("reviewed_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("extraction_model", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ai_extractions_call_id", "ai_extractions", ["call_id"])
    op.create_index("ix_ai_extractions_reviewed_by", "ai_extractions", ["reviewed_by"])

    # --- 13. worker_onboarding_calls ---
    op.create_table(
        "worker_onboarding_calls",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("worker_id", UUID(as_uuid=True), sa.ForeignKey("workers.id"), nullable=False),
        sa.Column("call_type", onboarding_call_type, nullable=False),
        sa.Column("vapi_call_id", sa.String(255), nullable=True),
        sa.Column("status", ai_call_status, nullable=False),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_worker_onboarding_calls_worker_id", "worker_onboarding_calls", ["worker_id"])

    # --- 14. sms_logs ---
    op.create_table(
        "sms_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("worker_id", UUID(as_uuid=True), sa.ForeignKey("workers.id"), nullable=True),
        sa.Column("match_id", UUID(as_uuid=True), sa.ForeignKey("matches.id"), nullable=True),
        sa.Column("direction", sms_direction, nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("twilio_sid", sa.String(255), nullable=True),
        sa.Column("status", sms_status, nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_sms_logs_worker_id", "sms_logs", ["worker_id"])
    op.create_index("ix_sms_logs_match_id", "sms_logs", ["match_id"])
    op.create_index("ix_sms_logs_status", "sms_logs", ["status"])

    # --- 15. ratings ---
    op.create_table(
        "ratings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("job_id", UUID(as_uuid=True), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("match_id", UUID(as_uuid=True), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("rated_by", rated_by, nullable=False),
        sa.Column("rating_score", sa.Integer(), nullable=False),
        sa.Column("review_text", sa.Text(), nullable=True),
        sa.Column("is_public", sa.Boolean(), default=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ratings_job_id", "ratings", ["job_id"])
    op.create_index("ix_ratings_match_id", "ratings", ["match_id"])

    # --- 16. payments ---
    op.create_table(
        "payments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("match_id", UUID(as_uuid=True), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(10), default="GTQ", nullable=False),
        sa.Column("payment_type", payment_type, nullable=False),
        sa.Column("status", payment_status, nullable=False),
        sa.Column("invoice_date", sa.Date(), nullable=True),
        sa.Column("paid_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_payments_match_id", "payments", ["match_id"])
    op.create_index("ix_payments_company_id", "payments", ["company_id"])
    op.create_index("ix_payments_status", "payments", ["status"])


def downgrade() -> None:
    # Drop tables in reverse dependency order
    op.drop_table("payments")
    op.drop_table("ratings")
    op.drop_table("sms_logs")
    op.drop_table("worker_onboarding_calls")
    op.drop_table("ai_extractions")
    op.drop_table("ai_calls")
    op.drop_table("counteroffers")
    op.drop_table("matches")
    op.drop_table("jobs")
    op.drop_table("reference_calls")
    op.drop_table("worker_references")
    op.drop_table("worker_trades")
    op.drop_table("worker_profiles")
    op.drop_table("workers")
    op.drop_table("companies")
    op.drop_table("users")

    # Drop enum types
    for enum_name in [
        "payment_status", "payment_type", "rated_by", "sms_status",
        "sms_direction", "onboarding_call_type", "extraction_final_status",
        "ai_call_status", "ai_call_type", "counteroffer_status",
        "counteroffer_proposed_by", "worker_reply", "match_status",
        "job_status", "reference_call_status", "reference_outcome",
        "skill_level_required", "skill_level", "trade", "profile_status",
        "language", "subscription_plan", "company_type", "user_role",
    ]:
        sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
