from flask import Blueprint, jsonify

from services.jwt_utils import jwt_required

billing_bp = Blueprint("billing", __name__)


@billing_bp.route("/billing/status", methods=["GET"])
@jwt_required(roles={"admin"})
def status():
    return jsonify({"status": "billing-ok"})

