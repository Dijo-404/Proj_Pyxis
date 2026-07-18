"""Shared SQLAlchemy declarative base for Pyxis persistence models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for all Pyxis relational models."""
