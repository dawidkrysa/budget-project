#!/usr/bin/env python3
from extensions import db
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4


# -------------------------------
# BaseModel
# -------------------------------
class BaseModel(db.Model):
    """Base model class for all database models providing common functionality."""
    __abstract__ = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self) -> dict:
        """Convert model instance to dictionary representation."""
        result = {}
        for c in self.__table__.columns:
            try:
                result[c.name] = getattr(self, c.name)
            except AttributeError:
                result[c.name] = None
        return result

    def __repr__(self):
        values = ", ".join(f"{c.name}={getattr(self, c.name)!r}" for c in self.__table__.columns)
        return f"<{self.__class__.__name__}({values})>"