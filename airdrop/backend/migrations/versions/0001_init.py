"""init

Revision ID: 0001_init
Revises:
Create Date: 2026-01-23

"""

from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("role", sa.Enum("USER","ADMIN","SYSTEM", name="userrole"), nullable=False, server_default="USER"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_seen", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"])

    op.create_table(
        "wallets",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("balance", sa.Numeric(20,8), nullable=False, server_default="0"),
    )

    op.create_table(
        "event_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event", sa.String(128), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_event_logs_event", "event_logs", ["event"])

    op.create_table(
        "token_config",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("price", sa.Numeric(20,8), nullable=False, server_default="1"),
        sa.Column("max_airdrop_per_user", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "feature_flags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(128), nullable=False, unique=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_feature_flags_key", "feature_flags", ["key"])

    op.create_table(
        "airdrops",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("amount", sa.Numeric(20,8), nullable=False),
        sa.Column("status", sa.Enum("PENDING","APPROVED","REJECTED", name="airdropstatus"), nullable=False, server_default="PENDING"),
        sa.Column("reason", sa.String(256), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_airdrops_user_id", "airdrops", ["user_id"])

def downgrade():
    op.drop_index("ix_airdrops_user_id", table_name="airdrops")
    op.drop_table("airdrops")
    op.drop_index("ix_feature_flags_key", table_name="feature_flags")
    op.drop_table("feature_flags")
    op.drop_table("token_config")
    op.drop_index("ix_event_logs_event", table_name="event_logs")
    op.drop_table("event_logs")
    op.drop_table("wallets")
    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS airdropstatus")
    op.execute("DROP TYPE IF EXISTS userrole")
