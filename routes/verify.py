from flask import Blueprint, jsonify

verify_bp = Blueprint("verify", __name__)


@verify_bp.route("/verify/ping", methods=["GET"])
def ping():
    return jsonify({"status": "verified"})

