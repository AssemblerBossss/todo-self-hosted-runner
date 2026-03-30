"""add full todo edit history

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-03-30 15:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "b8c9d0e1f2a3"
down_revision = "a7b8c9d0e1f2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "todo_edit_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("todo_id", sa.Integer(), nullable=False),
        sa.Column("editor_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("edited_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("details", sa.Text(), nullable=False),
        sa.Column("tag", sa.String(), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("image_path", sa.String(), nullable=True),
        sa.Column("spacy_summary", sa.Text(), nullable=True),
        sa.Column("llm_summary", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["todo_id"], ["todos.id"]),
        sa.ForeignKeyConstraint(["editor_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_todo_edit_history_todo_id",
        "todo_edit_history",
        ["todo_id"],
        unique=False,
    )
    op.create_index(
        "ix_todo_edit_history_editor_id",
        "todo_edit_history",
        ["editor_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_todo_edit_history_editor_id", table_name="todo_edit_history")
    op.drop_index("ix_todo_edit_history_todo_id", table_name="todo_edit_history")
    op.drop_table("todo_edit_history")
