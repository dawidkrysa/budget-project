#!/usr/bin/env python3
from extensions.database import db

class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    hidden = db.Column(db.Boolean, default=False)

    transactions = db.relationship('Transaction', back_populates='account')


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    main_category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    hidden = db.Column(db.Boolean, default=False)

    main_category = db.relationship('Category', remote_side=[id], backref='subcategories')
    transactions = db.relationship('Transaction', back_populates='category')
    budgets = db.relationship('Budget', back_populates='category')


class Budget(db.Model):
    __tablename__ = 'budget'

    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    assigned = db.Column(db.Numeric(15, 2), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    category = db.relationship('Category', back_populates='budgets')


class Payee(db.Model):
    __tablename__ = 'payees'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)

    transactions = db.relationship('Transaction', back_populates='payee')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.BigInteger, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    memo = db.Column(db.Text, nullable=True)
    payee_id = db.Column(db.BigInteger, db.ForeignKey('payees.id'), nullable=False)

    category = db.relationship('Category', back_populates='transactions')
    account = db.relationship('Account', back_populates='transactions')
    payee = db.relationship('Payee', back_populates='transactions')

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'amount': float(self.amount),  # convert Decimal to float for JSON
            'category': {
                'id': self.category.id,
                'name': self.category.name
            } if self.category else None,
            'account': {
                'id': self.account.id,
                'name': self.account.name
            } if self.account else None,
            'memo': self.memo,
            'payee': {
                'id': self.payee.id,
                'name': self.payee.name
            } if self.payee else None,
        }

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)




class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.BigInteger, primary_key=True)
    login = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    active = db.Column(db.Boolean, default=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False)