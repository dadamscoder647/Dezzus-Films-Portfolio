from models import User


def test_register_creates_user(client, app):
    response = client.post(
        "/auth/register",
        json={"email": "new@example.com", "password": "secret"},
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "token" in data

    with app.app_context():
        assert User.query.filter_by(email="new@example.com").one()


def test_login_returns_token(client, employer_user):
    response = client.post(
        "/auth/login",
        json={"email": "employer@example.com", "password": "password"},
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert "token" in payload
