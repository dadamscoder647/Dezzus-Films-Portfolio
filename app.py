import os
from typing import Optional

from flask import Flask

from extensions import db
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
    }
    app.config.update(default_config)
    if config:
        app.config.update(config)

    db.init_app(app)
    register_auth_error_handlers(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(verify_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(listings_bp)
    app.register_blueprint(billing_bp)

    @app.before_first_request
    def _create_tables():
        db.create_all()

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

