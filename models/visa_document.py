from typing import Any, Dict, Optional

from extensions import db
from .base import TimestampMixin


class VisaDocument(db.Model, TimestampMixin):
    __tablename__ = "visa_documents"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(100), nullable=False)
    status = db.Column(
        db.Enum("pending", "approved", "rejected", name="visa_document_status"),
        nullable=False,
        default="pending",
    )
    reviewer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    review_note = db.Column(db.Text, nullable=True)

    user = db.relationship(
        "User", foreign_keys=[user_id], back_populates="visa_documents", lazy=True
    )
    reviewer = db.relationship("User", foreign_keys=[reviewer_id], lazy=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "status": self.status,
            "reviewer_id": self.reviewer_id,
            "review_note": self.review_note,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @property
    def is_pending(self) -> bool:
        return self.status == "pending"

    def mark_reviewed(
        self, status: str, reviewer_id: Optional[int] = None, note: Optional[str] = None
    ) -> None:
        if status not in {"approved", "rejected"}:
            raise ValueError("Status must be 'approved' or 'rejected'")
        self.status = status
        self.reviewer_id = reviewer_id
        self.review_note = note
