from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def healthcheck():
    """Return a simple health check payload."""
    return jsonify({"status": "ok"})
