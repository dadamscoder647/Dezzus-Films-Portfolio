"""Test stub for flask_migrate when dependency is unavailable."""

from __future__ import annotations


class Migrate:  # pragma: no cover - minimal stub for tests
    def __init__(self, app=None, db=None):
        self.app = app
        self.db = db

    def init_app(self, app, db):
        self.app = app
        self.db = db
