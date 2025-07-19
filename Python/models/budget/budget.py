#!/usr/bin/env python3
from ..base import BaseModel, db, uuid

# -------------------------------
# Budget Model
# -------------------------------

class Budget(BaseModel):
    """
    Represents a budget.
    """
    __tablename__ = 'budgets'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.Text, nullable=True)

    accounts = db.relationship('Account', backref='budget')
    categories = db.relationship('Category', backref='budget')
    payees = db.relationship('Payee', backref='budget')
    transactions = db.relationship('Transaction', backref='budget')
    category_groups = db.relationship('CategoryGroup', backref='budget')
    months = db.relationship('Month', backref='budget')