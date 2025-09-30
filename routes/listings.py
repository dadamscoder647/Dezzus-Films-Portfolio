from flask import Blueprint, g, jsonify, request
from sqlalchemy import func

from extensions import db
from models import Application, Listing
from services.jwt_utils import jwt_required

listings_bp = Blueprint("listings", __name__)


def _apply_filters(query):
    category = request.args.get("category")
    company = request.args.get("company")
    location = request.args.get("location")
    remote = request.args.get("remote")

    if category:
        query = query.filter(func.lower(Listing.category) == category.lower())
    if company:
        query = query.filter(func.lower(Listing.company) == company.lower())
    if location:
        query = query.filter(func.lower(Listing.location) == location.lower())
    if remote is not None:
        remote_bool = remote.lower() in {"true", "1", "yes"}
        query = query.filter(Listing.is_remote.is_(remote_bool))

    return query


@listings_bp.route("/listings", methods=["GET"])
def index():
    query = Listing.query
    query = _apply_filters(query)
    listings = [listing.to_dict() for listing in query.order_by(Listing.created_at.desc())]
    return jsonify({"data": listings})


@listings_bp.route("/listings", methods=["POST"])
@jwt_required(roles={"admin", "employer"})
def create_listing():
    payload = request.get_json(silent=True) or {}
    title = payload.get("title")
    description = payload.get("description")
    company = payload.get("company")
    location = payload.get("location")
    category = payload.get("category")
    is_remote = bool(payload.get("is_remote", False))

    if not all([title, description, company, location]):
        return jsonify({"error": "Missing required fields"}), 400

    current_user = getattr(g, "current_user", None)

    listing = Listing(
        title=title,
        description=description,
        company=company,
        location=location,
        category=category,
        is_remote=is_remote,
        employer_id=current_user.id if current_user else None,
    )

    if listing.employer_id is None:
        return jsonify({"error": "Employer context missing"}), 400

    db.session.add(listing)
    db.session.commit()

    return jsonify({"data": listing.to_dict()}), 201


@listings_bp.route("/listings/<int:listing_id>", methods=["GET"])
def retrieve_listing(listing_id: int):
    listing = Listing.query.get_or_404(listing_id)
    return jsonify({"data": listing.to_dict()})


@listings_bp.route("/listings/<int:listing_id>", methods=["PATCH"])
@jwt_required(roles={"admin", "employer"})
def update_listing(listing_id: int):
    listing = Listing.query.get_or_404(listing_id)

    current_user = getattr(g, "current_user", None)
    if current_user and current_user.role == "employer" and listing.employer_id != current_user.id:
        return jsonify({"error": "You do not own this listing"}), 403

    payload = request.get_json(silent=True) or {}

    for field in ["title", "description", "company", "location", "category"]:
        if field in payload and payload[field] is not None:
            setattr(listing, field, payload[field])

    if "is_remote" in payload:
        listing.is_remote = bool(payload["is_remote"])

    db.session.commit()
    return jsonify({"data": listing.to_dict()})


@listings_bp.route("/listings/<int:listing_id>/apply", methods=["POST"])
@jwt_required()
def apply_to_listing(listing_id: int):
    listing = Listing.query.get_or_404(listing_id)
    payload = request.get_json(silent=True) or {}

    applicant_name = payload.get("applicant_name")
    applicant_email = payload.get("applicant_email")
    resume_url = payload.get("resume_url")
    cover_letter = payload.get("cover_letter")

    if not applicant_name or not applicant_email:
        return jsonify({"error": "Applicant name and email are required"}), 400

    current_user = getattr(g, "current_user", None)

    application = Application(
        applicant_name=applicant_name,
        applicant_email=applicant_email,
        resume_url=resume_url,
        cover_letter=cover_letter,
        listing=listing,
        applicant=current_user if current_user else None,
    )
    db.session.add(application)
    db.session.commit()

    return jsonify({"data": application.to_dict()}), 201

