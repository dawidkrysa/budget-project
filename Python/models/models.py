#!/usr/bin/env python3
from extensions.database import db
import uuid

# -------------------------------
# BaseModel
# -------------------------------
class BaseModel(db.Model):
    __abstract__ = True

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        values = ", ".join(f"{c.name}={getattr(self, c.name)!r}" for c in self.__table__.columns)
        return f"<{self.__class__.__name__}({values})>"

# -------------------------------
# Account Model
# -------------------------------
class Account(BaseModel):
    """
    Represents a financial account.
    """
    __tablename__ = 'accounts'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # UUID string
    name = db.Column(db.Text, nullable=False, unique=True)
    type_id = db.Column(db.String(36), db.ForeignKey('accountsType.id'), nullable=True)
    deleted = db.Column(db.Boolean, default=False)
    balance = db.Column(db.Numeric(15, 2), nullable=True)
    transfer_payee_id = db.Column(db.String(36), nullable=True)  # Should be a UUID too
    budget_id = db.Column(db.String(36), db.ForeignKey('budgets.id'), nullable=False)

    transactions = db.relationship('Transaction', back_populates='account')

# -------------------------------
# Category Model
# -------------------------------

class Category(BaseModel):
    """
    Represents a transaction category for a specific month.
    """
    __tablename__ = 'categories'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_name_id = db.Column(db.String(36), db.ForeignKey('category_names.id'), nullable=False)
    category_group_id = db.Column(db.String(36), db.ForeignKey('category_groups.id'), nullable=False)
    hidden = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)
    budget_id = db.Column(db.String(36), db.ForeignKey('budgets.id'), nullable=False)
    budgeted = db.Column(db.Numeric(15, 2), default=0)
    activity = db.Column(db.Numeric(15, 2), default=0)
    balance = db.Column(db.Numeric(15, 2), default=0)
    month_id = db.Column(db.String(36), db.ForeignKey('months.id'), nullable=False)

    transactions = db.relationship('Transaction', back_populates='category')
    category_group = db.relationship('CategoryGroup', back_populates='categories')
    month = db.relationship('Month', back_populates='categories')
    category_name = db.relationship('CategoryName', back_populates='categories')

class CategoryName(BaseModel):
    """
    Represents the category name (normalized across months).
    """
    __tablename__ = 'category_names'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.Text, nullable=False, unique=True)

    categories = db.relationship('Category', back_populates='category_name')

# -------------------------------
# CategoryGroup Model
# -------------------------------

class CategoryGroup(BaseModel):
    """
    Represents a group of categories.
    """
    __tablename__ = 'category_groups'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.Text, nullable=False, unique=True)
    deleted = db.Column(db.Boolean, default=False)
    budget_id = db.Column(db.String(36), db.ForeignKey('budgets.id'), nullable=False)

    categories = db.relationship('Category', back_populates='category_group')

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

# -------------------------------
# Month Model
# -------------------------------

class Month(BaseModel):
    """
    Represents a month for budgeting.
    """
    __tablename__ = 'months'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    month = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, primary_key=True)
    budgeted = db.Column(db.Numeric(15, 2), default=0)
    activity = db.Column(db.Numeric(15, 2), default=0)
    to_be_budgeted = db.Column(db.Numeric(15, 2), default=0)
    deleted = db.Column(db.Boolean, default=False)
    budget_id = db.Column(db.String(36), db.ForeignKey('budgets.id'), nullable=False)

    categories = db.relationship('Category', back_populates='month')

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

# -------------------------------
# AccountsType Model
# -------------------------------

class AccountsType(BaseModel):
    """
    Represents the account type.
    """
    __tablename__ = 'accountsType'

    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.Text, nullable=False)

    accounts = db.relationship('Account', backref='accountsType')
