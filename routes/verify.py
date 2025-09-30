"""Routes for managing user verification documents."""

from __future__ import annotations

import os
from typing import Any, Dict

from flask import (
    Blueprint,
    abort,
    current_app,
    g,
    jsonify,
    request,
    send_file,
)

from extensions import db
from models import User, VisaDocument
from services.jwt_utils import jwt_required
from storage.local_storage import LocalStorage

verify_bp = Blueprint("verify", __name__)


def _get_storage() -> LocalStorage:
    upload_dir = current_app.config["UPLOAD_DIR"]
    return LocalStorage(upload_dir)


def _validate_file(file_storage) -> None:
    if file_storage is None:
        abort(400, description="Missing document upload")

    allowed_types = set(current_app.config.get("ALLOWED_UPLOAD_TYPES", []))
    if file_storage.mimetype not in allowed_types:
        abort(400, description="Unsupported file type")

    max_size = current_app.config.get("MAX_UPLOAD_SIZE")
    content_length = request.content_length
    if max_size and content_length and content_length > max_size:
        abort(413, description="Uploaded file exceeds maximum size")

    # Ensure stream size is within limits when content_length is absent.
    if max_size:
        stream = file_storage.stream
        current_pos = stream.tell()
        stream.seek(0, os.SEEK_END)
        size = stream.tell()
        stream.seek(0)
        if size > max_size:
            abort(413, description="Uploaded file exceeds maximum size")
        stream.seek(current_pos)


@verify_bp.route("/verify/upload", methods=["POST"])
@jwt_required()
def upload_document() -> Any:
    file_storage = request.files.get("document")
    _validate_file(file_storage)

    waiver_flag = request.form.get("waiver", "false").lower() in {
        "true",
        "1",
        "yes",
    }

    storage = _get_storage()
    filename, file_path = storage.save(file_storage)

    user: User = g.current_user
    document = VisaDocument(
        user_id=user.id,
        filename=filename,
        file_path=file_path,
        file_type=file_storage.mimetype,
        status="pending",
    )
    user.verification_status = "pending"

    db.session.add(document)
    db.session.commit()

    response: Dict[str, Any] = {
        "message": "Document uploaded successfully",
        "document": document.to_dict(),
        "waiver": waiver_flag,
        "verification_status": user.verification_status,
    }
    return jsonify(response), 201


@verify_bp.route("/verify/status", methods=["GET"])
@jwt_required()
def verification_status() -> Any:
    user: User = g.current_user
    latest_document = (
        VisaDocument.query.filter_by(user_id=user.id)
        .order_by(VisaDocument.created_at.desc())
        .first()
    )
    response: Dict[str, Any] = {
        "verification_status": user.verification_status,
        "latest_document": latest_document.to_dict() if latest_document else None,
    }
    return jsonify(response)


@verify_bp.route("/verify/doc/<int:document_id>", methods=["GET"])
@jwt_required(roles=["admin"])
def get_document(document_id: int):
    document = VisaDocument.query.get_or_404(document_id)
    if not os.path.exists(document.file_path):
        abort(404, description="Stored file not found")

    return send_file(
        document.file_path,
        as_attachment=True,
        download_name=document.filename,
    )


@verify_bp.route("/verify/<int:document_id>/approve", methods=["POST"])
@jwt_required(roles=["admin"])
def approve_document(document_id: int):
    document = VisaDocument.query.get_or_404(document_id)
    admin_user: User = g.current_user

    document.mark_reviewed("approved", reviewer_id=admin_user.id)
    document.user.verification_status = "approved"

    db.session.commit()

    response = {
        "message": "Document approved",
        "document": document.to_dict(),
        "verification_status": document.user.verification_status,
    }
    return jsonify(response)


@verify_bp.route("/verify/<int:document_id>/reject", methods=["POST"])
@jwt_required(roles=["admin"])
def reject_document(document_id: int):
    document = VisaDocument.query.get_or_404(document_id)
    admin_user: User = g.current_user

    payload = request.get_json(silent=True) or {}
    review_note = payload.get("review_note")
    if not review_note:
        abort(400, description="review_note is required for rejection")

    document.mark_reviewed("rejected", reviewer_id=admin_user.id, note=review_note)
    document.user.verification_status = "rejected"

    db.session.commit()

    response = {
        "message": "Document rejected",
        "document": document.to_dict(),
        "verification_status": document.user.verification_status,
    }
    return jsonify(response)
