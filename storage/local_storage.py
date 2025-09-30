"""Local filesystem storage backend for uploads."""

from __future__ import annotations

import os
import uuid
from typing import Tuple

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from .abstract_storage import AbstractStorage


class LocalStorage(AbstractStorage):
    """Store uploaded files on the local filesystem."""

    def __init__(self, upload_dir: str) -> None:
        self.upload_dir = upload_dir

    def save(self, file_storage: FileStorage) -> Tuple[str, str]:
        if not file_storage or not file_storage.filename:
            raise ValueError("A valid file must be provided")

        original_name = secure_filename(file_storage.filename)
        name, ext = os.path.splitext(original_name)
        unique_name = f"{name or 'upload'}_{uuid.uuid4().hex}{ext}"

        os.makedirs(self.upload_dir, exist_ok=True)
        file_path = os.path.join(self.upload_dir, unique_name)
        file_storage.save(file_path)

        return unique_name, file_path
