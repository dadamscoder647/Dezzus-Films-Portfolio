from typing import Any, Dict, Optional

from extensions import db
from .base import TimestampMixin


class User(db.Model, TimestampMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="applicant")
    verification_status = db.Column(db.String(20), nullable=False, default="unverified")
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    listings = db.relationship("Listing", back_populates="employer", lazy=True)
    applications = db.relationship("Application", back_populates="applicant", lazy=True)
    visa_documents = db.relationship(
        "VisaDocument", back_populates="user", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role,
            "verification_status": self.verification_status,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def mark_verified(self) -> None:
        """Mark the user as verified and active."""

        self.verification_status = "verified"
        self.is_active = True

    def mark_unverified(self, note: Optional[str] = None) -> None:
        """Mark the user as unverified and optionally log a note.

        Args:
            note: Optional note about the unverification reason (unused placeholder).
        """

        self.verification_status = "unverified"
        self.is_active = False
        if note:
            # Placeholder for future logging or auditing integrations.
            setattr(self, "_last_unverification_note", note)
