import pytest

import werkzeug

from app import create_app
from extensions import db
from models import User


if not hasattr(werkzeug, "__version__"):
    werkzeug.__version__ = "3"


@pytest.fixture()
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def admin_user(app):
    from werkzeug.security import generate_password_hash

    user = User(email="admin@example.com", password_hash=generate_password_hash("password"), role="admin")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def employer_user(app):
    from werkzeug.security import generate_password_hash

    user = User(email="employer@example.com", password_hash=generate_password_hash("password"), role="employer")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def applicant_user(app):
    from werkzeug.security import generate_password_hash

    user = User(email="applicant@example.com", password_hash=generate_password_hash("password"), role="applicant")
    db.session.add(user)
    db.session.commit()
    return user

