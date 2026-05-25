"""012_monthly_tasks

Revision ID: 4dfc2d0f3a12
Revises: 10e59cbc5c5d
Create Date: 2026-05-26 01:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4dfc2d0f3a12"
down_revision: Union[str, None] = "10e59cbc5c5d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "monthly_tasks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("action_type", sa.String(length=32), nullable=False),
        sa.Column("action_label", sa.String(length=64), nullable=False),
        sa.Column("action_params", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_monthly_tasks_month"), "monthly_tasks", ["month"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_monthly_tasks_month"), table_name="monthly_tasks")
    op.drop_table("monthly_tasks")
