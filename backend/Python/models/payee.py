#!/usr/bin/env python3
from models.base import BaseModel, db, uuid4, UUID

# -------------------------------
# Payee Model
# -------------------------------

class Payee(BaseModel):
    """
    Represents a payee entity.
    """
    __tablename__ = 'payees'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = db.Column(db.Text, nullable=False, unique=True)
    transfer_account_id = db.Column(db.String(36), db.ForeignKey('accounts.id'), nullable=True)
    deleted = db.Column(db.Boolean, default=False)
    budget_id = db.Column(db.String(36), db.ForeignKey('budgets.id'), nullable=False)

    transactions = db.relationship('Transaction', back_populates='payee')
    transfer_account = db.relationship('Account')