#!/usr/bin/env python3
from models.base import BaseModel, db, uuid

# -------------------------------
# Transaction Model
# -------------------------------
class Transaction(BaseModel):
    """
    Represents a financial transaction.
    """
    __tablename__ = 'transactions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date = db.Column(db.Date, nullable=False)
    category_id = db.Column(db.String(36), db.ForeignKey('categories.id'), nullable=True)
    account_id = db.Column(db.String(36), db.ForeignKey('accounts.id'), nullable=False)
    payee_id = db.Column(db.String(36), db.ForeignKey('payees.id'), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    memo = db.Column(db.Text, nullable=True)
    deleted = db.Column(db.Boolean, default=False)
    budget_id = db.Column(db.String(36), db.ForeignKey('budgets.id'), nullable=False)

    category = db.relationship('Category', back_populates='transactions')
    account = db.relationship('Account', back_populates='transactions')
    payee = db.relationship('Payee', back_populates='transactions')