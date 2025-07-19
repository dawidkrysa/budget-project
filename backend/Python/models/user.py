#!/usr/bin/env python3
from models.base import BaseModel, db, uuid

# -------------------------------
# User Model
# -------------------------------

class User(BaseModel):
    """
    Represents a user of the system.
    """
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    login = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    active = db.Column(db.Boolean, default=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False)