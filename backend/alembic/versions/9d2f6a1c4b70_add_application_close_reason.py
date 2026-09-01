"""add application close reason and closed time

Revision ID: 9d2f6a1c4b70
Revises: f871c4025951
Create Date: 2026-09-01 13:30:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9d2f6a1c4b70"
down_revision: Union[str, None] = "f871c4025951"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("applications") as batch_op:
        batch_op.add_column(sa.Column("close_reason", sa.String(length=40), nullable=True))
        batch_op.add_column(sa.Column("closed_at", sa.DateTime(), nullable=True))
        batch_op.create_index("ix_applications_close_reason", ["close_reason"], unique=False)
        batch_op.create_index("ix_applications_closed_at", ["closed_at"], unique=False)

    with op.batch_alter_table("application_status_logs") as batch_op:
        batch_op.add_column(sa.Column("close_reason", sa.String(length=40), nullable=True))

    # 对旧数据做保守回填。无法可靠判断的统一标记 other，避免伪造精确原因。
    op.execute(
        "UPDATE applications SET close_reason = 'resume_rejected', closed_at = updated_at "
        "WHERE status = 'resume_rejected'"
    )
    op.execute(
        "UPDATE applications SET close_reason = 'offer_declined', closed_at = updated_at "
        "WHERE status = 'rejected'"
    )
    op.execute(
        "UPDATE applications SET close_reason = 'other', closed_at = updated_at "
        "WHERE status = 'ended' AND close_reason IS NULL"
    )


def downgrade() -> None:
    with op.batch_alter_table("application_status_logs") as batch_op:
        batch_op.drop_column("close_reason")

    with op.batch_alter_table("applications") as batch_op:
        batch_op.drop_index("ix_applications_closed_at")
        batch_op.drop_index("ix_applications_close_reason")
        batch_op.drop_column("closed_at")
        batch_op.drop_column("close_reason")
