from __future__ import annotations

from io import BytesIO

import pytest

from extensions import db
from models import User, VisaDocument
from services.jwt_utils import encode_token


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_upload_requires_jwt(client, app, tmp_path):
    app.config["UPLOAD_DIR"] = str(tmp_path / "uploads")

    response = client.post("/verify/upload")

    assert response.status_code == 401


@pytest.mark.usefixtures("applicant_user")
def test_upload_and_status(client, app, tmp_path):
    app.config["UPLOAD_DIR"] = str(tmp_path / "uploads")

    login_response = client.post(
        "/auth/login",
        json={"email": "applicant@example.com", "password": "password"},
    )
    assert login_response.status_code == 200
    token = login_response.get_json()["token"]

    upload_response = client.post(
        "/verify/upload",
        data={
            "document": (
                BytesIO(b"fake image data"),
                "document.jpg",
                "image/jpeg",
            )
        },
        content_type="multipart/form-data",
        headers=_auth_header(token),
    )

    assert upload_response.status_code == 201
    payload = upload_response.get_json()
    assert payload["document"]["status"] == "pending"
    assert payload["verification_status"] == "pending"

    status_response = client.get(
        "/verify/status",
        headers=_auth_header(token),
    )

    assert status_response.status_code == 200
    status_payload = status_response.get_json()
    assert status_payload["verification_status"] == "pending"
    assert status_payload["latest_document"]["status"] == "pending"


@pytest.mark.usefixtures("admin_user")
def test_admin_approve(client, app, tmp_path, applicant_user):
    app.config["UPLOAD_DIR"] = str(tmp_path / "uploads")

    with app.app_context():
        document = VisaDocument(
            user_id=applicant_user.id,
            filename="document.jpg",
            file_path=str(tmp_path / "uploads" / "document.jpg"),
            file_type="image/jpeg",
            status="pending",
        )
        db.session.add(document)
        db.session.commit()
        document_id = document.id

        admin = User.query.filter_by(email="admin@example.com").first()
        assert admin is not None
        admin_token = encode_token(admin)

    response = client.post(
        f"/verify/{document_id}/approve",
        headers=_auth_header(admin_token),
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["document"]["status"] == "approved"
    assert data["verification_status"] == "approved"

    with app.app_context():
        refreshed_user = db.session.get(User, applicant_user.id)
        assert refreshed_user is not None
        assert refreshed_user.verification_status == "approved"


@pytest.mark.usefixtures("admin_user")
def test_admin_reject_with_note(client, app, tmp_path, applicant_user):
    app.config["UPLOAD_DIR"] = str(tmp_path / "uploads")

    with app.app_context():
        document = VisaDocument(
            user_id=applicant_user.id,
            filename="document.jpg",
            file_path=str(tmp_path / "uploads" / "document.jpg"),
            file_type="image/jpeg",
            status="pending",
        )
        db.session.add(document)
        db.session.commit()
        document_id = document.id

        admin = User.query.filter_by(email="admin@example.com").first()
        assert admin is not None
        admin_token = encode_token(admin)

    note = "Document incomplete"
    response = client.post(
        f"/verify/{document_id}/reject",
        json={"review_note": note},
        headers=_auth_header(admin_token),
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["document"]["status"] == "rejected"
    assert data["document"]["review_note"] == note
    assert data["verification_status"] in {"rejected", "unverified"}

    with app.app_context():
        refreshed_user = db.session.get(User, applicant_user.id)
        refreshed_document = db.session.get(VisaDocument, document_id)
        assert refreshed_user is not None
        assert refreshed_document is not None
        assert refreshed_document.review_note == note
        assert refreshed_user.verification_status in {"rejected", "unverified"}
