from flask_sqlalchemy import SQLAlchemy

# Shared SQLAlchemy instance for the application
# Imported by modules that require database access.
db = SQLAlchemy()
