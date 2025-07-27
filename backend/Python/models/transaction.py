#!/usr/bin/env python3
from typing import override

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


    def to_dict(self, expand: list[str] = None) -> dict:
        """Convert model instance to dictionary representation with optional expand."""
        expand = expand or []
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}

        if "account" in expand and self.account:
            result["account"] = self.account.to_dict()  # Make sure Account model has to_dict()
            result.pop("account_id", None)
        if "category" in expand and self.category:
            result["category"] = self.category.to_dict()
            result["category"]["category_name"] = self.category.category_name.name
            result.pop("category_id", None)
        if "payee" in expand and self.payee:
            result["payee"] = self.payee.to_dict()
            result.pop("payee_id", None)

        return result