"""Application configuration defaults."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
DEFAULT_UPLOAD_DIR = os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads"))

MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 10 * 1024 * 1024))
ALLOWED_UPLOAD_TYPES = [
    mime.strip()
    for mime in os.getenv(
        "ALLOWED_UPLOAD_TYPES", "image/jpeg,image/png,application/pdf"
    ).split(",")
    if mime.strip()
]

UPLOAD_DIR = DEFAULT_UPLOAD_DIR
