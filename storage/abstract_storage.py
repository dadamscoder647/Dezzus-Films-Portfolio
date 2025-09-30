"""Abstract storage backend definitions for file uploads."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple

from werkzeug.datastructures import FileStorage


class AbstractStorage(ABC):
    """Interface for storage backends used by the application."""

    @abstractmethod
    def save(self, file_storage: FileStorage) -> Tuple[str, str]:
        """Persist a file and return a tuple of (filename, file_path)."""

        raise NotImplementedError
