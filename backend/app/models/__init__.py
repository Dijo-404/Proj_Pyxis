"""SQLAlchemy persistence models.

Concrete mappings are added alongside the first database migration so model and
schema evolution stay synchronized.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for all Pyxis relational models."""
