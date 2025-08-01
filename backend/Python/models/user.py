#!/usr/bin/env python3
from models.base import BaseModel, db, UUID, uuid4


# -------------------------------
# User Model
# -------------------------------

class User(BaseModel):
    """
    Represents a user of the system.
    """
    __tablename__ = 'users'
    __table_args__ = (
        db.UniqueConstraint('email', name='users_email_key'),
        db.UniqueConstraint('login', name='users_login_key'),
    )

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    login = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    active = db.Column(db.Boolean, default=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False)