#!/usr/bin/env python3
from Python import db
import uuid

# -------------------------------
# BaseModel
# -------------------------------
class BaseModel(db.Model):
    __abstract__ = True

    def __init__(self):
        self.__table__ = None

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        values = ", ".join(f"{c.name}={getattr(self, c.name)!r}" for c in self.__table__.columns)
        return f"<{self.__class__.__name__}({values})>"