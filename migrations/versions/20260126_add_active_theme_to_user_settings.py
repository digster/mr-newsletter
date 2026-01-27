"""add active_theme to user_settings

Revision ID: 7a8b9c0d1e2f
Revises: 60ea93dbedf5
Create Date: 2026-01-26 10:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7a8b9c0d1e2f"
down_revision: Union[str, None] = "60ea93dbedf5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""
    with op.batch_alter_table("user_settings", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "active_theme",
                sa.String(length=255),
                nullable=True,
                server_default="default.json",
            )
        )


def downgrade() -> None:
    """Downgrade database schema."""
    with op.batch_alter_table("user_settings", schema=None) as batch_op:
        batch_op.drop_column("active_theme")
