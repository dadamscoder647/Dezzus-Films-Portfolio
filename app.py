import os
from typing import Optional

from flask import Flask

from config import ALLOWED_UPLOAD_TYPES, MAX_UPLOAD_SIZE, UPLOAD_DIR
from extensions import db, migrate
from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.billing import billing_bp
from routes.listings import listings_bp
from routes.verify import verify_bp
from services.jwt_utils import register_auth_error_handlers


def create_app(config: Optional[dict] = None) -> Flask:
    app = Flask(__name__)

    default_config = {
        "SQLALCHEMY_DATABASE_URI": os.environ.get("DATABASE_URL", "sqlite:///app.db"),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": os.environ.get("SECRET_KEY", "dev-secret-key"),
        "JWT_ALGORITHM": os.environ.get("JWT_ALGORITHM", "HS256"),
        "UPLOAD_DIR": os.environ.get("UPLOAD_DIR", UPLOAD_DIR),
        "MAX_UPLOAD_SIZE": MAX_UPLOAD_SIZE,
        "ALLOWED_UPLOAD_TYPES": ALLOWED_UPLOAD_TYPES,
    }
    app.config.update(default_config)
    if config:
        app.config.update(config)

    db.init_app(app)
    migrate.init_app(app, db)
    register_auth_error_handlers(app)

    os.makedirs(app.config["UPLOAD_DIR"], exist_ok=True)

    app.register_blueprint(auth_bp)
    app.register_blueprint(verify_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(listings_bp)
    app.register_blueprint(billing_bp)

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
