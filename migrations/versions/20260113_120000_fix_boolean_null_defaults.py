"""Fix boolean NULL defaults and add server defaults.

Revision ID: b7c84d62fa12
Revises: a5a1ab541a29
Create Date: 2026-01-13 12:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b7c84d62fa12"
down_revision: Union[str, None] = "a5a1ab541a29"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Step 1: Backfill NULL values in emails table
    op.execute("UPDATE emails SET is_read = 0 WHERE is_read IS NULL")
    op.execute("UPDATE emails SET is_starred = 0 WHERE is_starred IS NULL")
    op.execute("UPDATE emails SET is_archived = 0 WHERE is_archived IS NULL")

    # Step 2: Backfill NULL values in newsletters table
    op.execute("UPDATE newsletters SET is_active = 1 WHERE is_active IS NULL")
    op.execute("UPDATE newsletters SET auto_fetch_enabled = 1 WHERE auto_fetch_enabled IS NULL")

    # Step 3: Add NOT NULL constraints and server defaults for emails
    with op.batch_alter_table("emails", schema=None) as batch_op:
        batch_op.alter_column(
            "is_read",
            existing_type=sa.BOOLEAN(),
            nullable=False,
            server_default=sa.text("0"),
        )
        batch_op.alter_column(
            "is_starred",
            existing_type=sa.BOOLEAN(),
            nullable=False,
            server_default=sa.text("0"),
        )
        batch_op.alter_column(
            "is_archived",
            existing_type=sa.BOOLEAN(),
            nullable=False,
            server_default=sa.text("0"),
        )

    # Step 4: Add NOT NULL constraints and server defaults for newsletters
    with op.batch_alter_table("newsletters", schema=None) as batch_op:
        batch_op.alter_column(
            "is_active",
            existing_type=sa.BOOLEAN(),
            nullable=False,
            server_default=sa.text("1"),
        )
        batch_op.alter_column(
            "auto_fetch_enabled",
            existing_type=sa.BOOLEAN(),
            nullable=False,
            server_default=sa.text("1"),
        )


def downgrade() -> None:
    """Downgrade database schema."""
    # Remove NOT NULL constraints (restore to nullable)
    with op.batch_alter_table("emails", schema=None) as batch_op:
        batch_op.alter_column(
            "is_read",
            existing_type=sa.BOOLEAN(),
            nullable=True,
            server_default=None,
        )
        batch_op.alter_column(
            "is_starred",
            existing_type=sa.BOOLEAN(),
            nullable=True,
            server_default=None,
        )
        batch_op.alter_column(
            "is_archived",
            existing_type=sa.BOOLEAN(),
            nullable=True,
            server_default=None,
        )

    with op.batch_alter_table("newsletters", schema=None) as batch_op:
        batch_op.alter_column(
            "is_active",
            existing_type=sa.BOOLEAN(),
            nullable=True,
            server_default=None,
        )
        batch_op.alter_column(
            "auto_fetch_enabled",
            existing_type=sa.BOOLEAN(),
            nullable=True,
            server_default=None,
        )
