#!/usr/bin/env python3
from ..base import BaseModel, db, uuid

# -------------------------------
# Payee Model
# -------------------------------

class Payee(BaseModel):
    """
    Represents a payee entity.
    """
    __tablename__ = 'payees'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.Text, nullable=False, unique=True)
    transfer_account_id = db.Column(db.String(36), db.ForeignKey('accounts.id'), nullable=True)
    deleted = db.Column(db.Boolean, default=False)
    budget_id = db.Column(db.String(36), db.ForeignKey('budgets.id'), nullable=False)

    transactions = db.relationship('Transaction', back_populates='payee')
    transfer_account = db.relationship('Account')