"""Add visa documents table and user verification fields

Revision ID: 202401091200
Revises: 
Create Date: 2024-01-09 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "202401091200"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "verification_status",
            sa.String(length=20),
            nullable=False,
            server_default="unverified",
        ),
    )
    op.add_column(
        "users",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    op.create_table(
        "visa_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_type", sa.String(length=100), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "approved", "rejected", name="visa_document_status"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("reviewer_id", sa.Integer(), nullable=True),
        sa.Column("review_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            server_onupdate=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["reviewer_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_visa_documents_status"), "visa_documents", ["status"], unique=False
    )

    op.alter_column(
        "users",
        "verification_status",
        server_default=None,
        existing_type=sa.String(length=20),
    )
    op.alter_column(
        "users",
        "is_active",
        server_default=None,
        existing_type=sa.Boolean(),
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_visa_documents_status"), table_name="visa_documents")
    op.drop_table("visa_documents")

    op.drop_column("users", "is_active")
    op.drop_column("users", "verification_status")

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP TYPE IF EXISTS visa_document_status")
