from typing import Any, Dict

from extensions import db
from .base import TimestampMixin


class Listing(db.Model, TimestampMixin):
    __tablename__ = "listings"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    company = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    is_remote = db.Column(db.Boolean, default=False, nullable=False)

    employer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    employer = db.relationship("User", back_populates="listings", lazy=True)

    applications = db.relationship("Application", back_populates="listing", lazy=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "company": self.company,
            "location": self.location,
            "category": self.category,
            "is_remote": self.is_remote,
            "employer_id": self.employer_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
