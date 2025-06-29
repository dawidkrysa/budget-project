#!/usr/bin/env python3
from extensions.database import db

class Transaction(db.Model):
    __tablename__ = 'transactions_view'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    account_name = db.Column(db.String)
    payee_name = db.Column(db.String)
    category_name = db.Column(db.String)
    memo = db.Column(db.String)
    amount = db.Column(db.Numeric)