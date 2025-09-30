from datetime import datetime, timedelta
from functools import wraps
from typing import Iterable, Optional

import jwt
from flask import current_app, g, jsonify, request
from models import User


class AuthError(Exception):
    """Custom exception for authentication issues."""

    def __init__(self, message: str, status_code: int = 401) -> None:
        super().__init__(message)
        self.status_code = status_code


def _get_secret() -> str:
    secret = current_app.config.get("SECRET_KEY")
    if not secret:
        raise RuntimeError("SECRET_KEY must be configured for JWT support")
    return secret


def encode_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
    algorithm = current_app.config.get("JWT_ALGORITHM", "HS256")
    expires = expires_delta or timedelta(hours=1)
    payload = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + expires,
    }
    return jwt.encode(payload, _get_secret(), algorithm=algorithm)


def decode_token(token: str) -> dict:
    algorithm = current_app.config.get("JWT_ALGORITHM", "HS256")
    return jwt.decode(token, _get_secret(), algorithms=[algorithm])


def jwt_required(roles: Optional[Iterable[str]] = None):
    """Decorator ensuring the presence of a valid JWT token."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                raise AuthError("Authorization header missing or malformed", 401)

            token = auth_header.split(" ", 1)[1]
            try:
                payload = decode_token(token)
            except jwt.ExpiredSignatureError as exc:
                raise AuthError("Token has expired", 401) from exc
            except jwt.InvalidTokenError as exc:
                raise AuthError("Invalid token", 401) from exc

            user = User.query.get(payload.get("sub"))
            if not user:
                raise AuthError("User not found", 401)

            if roles is not None and user.role not in roles:
                raise AuthError("Insufficient permissions", 403)

            g.current_user = user
            try:
                return fn(*args, **kwargs)
            finally:
                g.pop("current_user", None)

        return wrapper

    return decorator


def register_auth_error_handlers(app):
    """Attach error handlers for authentication errors to the Flask app."""

    @app.errorhandler(AuthError)
    def handle_auth_error(error: AuthError):  # type: ignore[override]
        response = jsonify({"error": str(error)})
        response.status_code = getattr(error, "status_code", 401)
        return response

    @app.errorhandler(jwt.InvalidTokenError)
    def handle_invalid_token(error):  # type: ignore[override]
        response = jsonify({"error": "Invalid token"})
        response.status_code = 401
        return response

