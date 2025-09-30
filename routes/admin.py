from flask import Blueprint, jsonify

from services.jwt_utils import jwt_required

admin_bp = Blueprint("admin_verify", __name__)


@admin_bp.route("/admin/health", methods=["GET"])
@jwt_required(roles={"admin"})
def health_check():
    return jsonify({"status": "admin-ok"})


@admin_bp.route("/admin/listings", methods=["GET"])
@jwt_required(roles={"admin"})
def list_all():
    from models import Listing  # Imported lazily to avoid circular import

    listings = [listing.to_dict() for listing in Listing.query.order_by(Listing.created_at.desc())]
    return jsonify({"data": listings})

