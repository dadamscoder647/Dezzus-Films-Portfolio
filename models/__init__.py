from datetime import datetime
from typing import Any, Dict

from extensions import db


class TimestampMixin:
    """Mixin providing created/updated timestamps."""

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class User(db.Model, TimestampMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="applicant")

    listings = db.relationship("Listing", back_populates="employer", lazy=True)
    applications = db.relationship("Application", back_populates="applicant", lazy=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


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
