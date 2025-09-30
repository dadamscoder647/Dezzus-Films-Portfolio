from werkzeug.security import check_password_hash

from models import User


def test_register_creates_user_and_hashes_password(client, app):
    response = client.post(
        "/auth/register",
        json={"email": "NewUser@example.com", "password": "secure123", "role": "employer"},
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "token" in data

    with app.app_context():
        user = User.query.filter_by(email="newuser@example.com").first()
        assert user is not None
        assert user.role == "employer"
        assert check_password_hash(user.password_hash, "secure123")


def test_register_rejects_duplicate_email_case_insensitive(client):
    response = client.post(
        "/auth/register",
        json={"email": "duplicate@example.com", "password": "pass"},
    )
    assert response.status_code == 201

    duplicate = client.post(
        "/auth/register",
        json={"email": "Duplicate@Example.com", "password": "pass"},
    )
    assert duplicate.status_code == 409


def test_login_returns_token(client, employer_user):
    response = client.post(
        "/auth/login",
        json={"email": "Employer@example.com", "password": "password"},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert "token" in payload


def test_login_rejects_wrong_password(client, employer_user):
    response = client.post(
        "/auth/login",
        json={"email": "employer@example.com", "password": "wrong"},
    )
    assert response.status_code == 401

