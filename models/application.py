from typing import Any, Dict

from extensions import db
from .base import TimestampMixin


class Application(db.Model, TimestampMixin):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    applicant_name = db.Column(db.String(200), nullable=False)
    applicant_email = db.Column(db.String(255), nullable=False)
    resume_url = db.Column(db.String(500), nullable=True)
    cover_letter = db.Column(db.Text, nullable=True)

    listing_id = db.Column(db.Integer, db.ForeignKey("listings.id"), nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    listing = db.relationship("Listing", back_populates="applications", lazy=True)
    applicant = db.relationship("User", back_populates="applications", lazy=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "applicant_name": self.applicant_name,
            "applicant_email": self.applicant_email,
            "resume_url": self.resume_url,
            "cover_letter": self.cover_letter,
            "listing_id": self.listing_id,
            "applicant_id": self.applicant_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
