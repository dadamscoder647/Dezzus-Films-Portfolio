from typing import Optional

from flask import Blueprint, jsonify, request
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from models import User
from services.jwt_utils import encode_token

auth_bp = Blueprint("auth", __name__)


def _normalize_email(email: str) -> str:
    return email.strip().lower()


@auth_bp.route("/auth/register", methods=["POST"])
def register():
    payload = request.get_json(silent=True) or {}
    email: Optional[str] = payload.get("email")
    password: Optional[str] = payload.get("password")
    role: str = payload.get("role", "applicant")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    normalized_email = _normalize_email(email)

    existing = User.query.filter(func.lower(User.email) == normalized_email.lower()).first()
    if existing:
        return jsonify({"error": "Email already registered"}), 409

    hashed_password = generate_password_hash(password)
    user = User(email=normalized_email, password_hash=hashed_password, role=role)
    db.session.add(user)
    db.session.commit()

    token = encode_token(user)
    return (
        jsonify(
            {
                "message": "Registration successful",
                "token": token,
                "user": user.to_dict(),
            }
        ),
        201,
    )


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    payload = request.get_json(silent=True) or {}
    email: Optional[str] = payload.get("email")
    password: Optional[str] = payload.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    normalized_email = _normalize_email(email)

    user = User.query.filter(func.lower(User.email) == normalized_email.lower()).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = encode_token(user)
    return jsonify({"token": token, "user": user.to_dict()}), 200


@auth_bp.route("/auth/profile", methods=["GET"])
def profile():
    return jsonify({"status": "ok"}), 200

