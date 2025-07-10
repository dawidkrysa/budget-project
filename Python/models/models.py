#!/usr/bin/env python3
from extensions.database import db


# -------------------------------
# Account Model
# -------------------------------

class Account(db.Model):
    """
    Represents a financial account.
    Attributes:
        id (int): Primary key.
        name (str): Account name, unique and required.
        hidden (bool): Flag to hide the account.
        transactions (list): List of associated Transaction objects.
    """
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    hidden = db.Column(db.Boolean, default=False)

    transactions = db.relationship('Transaction', back_populates='account')


# -------------------------------
# Category Model
# -------------------------------

class Category(db.Model):
    """
    Represents a transaction category, optionally linked to a main category.
    Attributes:
        id (int): Primary key.
        name (str): Category name, unique and required.
        main_category_id (int): Foreign key to parent category.
        hidden (bool): Flag to hide the category.
        main_category (Category): Parent category relationship.
        subcategories (list): List of subcategories.
        transactions (list): List of associated Transaction objects.
        budgets (list): List of associated Budget objects.
    """
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    main_category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    hidden = db.Column(db.Boolean, default=False)

    main_category = db.relationship('Category', remote_side=[id], backref='subcategories')
    transactions = db.relationship('Transaction', back_populates='category')
    budgets = db.relationship('Budget', back_populates='category')


# -------------------------------
# Budget Model
# -------------------------------

class Budget(db.Model):
    """
    Represents budget allocation for a category in a specific month and year.
    Attributes:
        id (int): Primary key.
        month (int): Month of the budget.
        year (int): Year of the budget.
        assigned (Decimal): Amount assigned to the budget.
        category_id (int): Foreign key to the associated category.
        category (Category): Relationship to Category model.
    """
    __tablename__ = 'budget'

    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    assigned = db.Column(db.Numeric(15, 2), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    category = db.relationship('Category', back_populates='budgets')

    def to_dict(self):
        """
        Converts the Budget object to a dictionary.
        Returns:
            dict: Dictionary with column names as keys and attribute values.
        """
        data = {}
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        data['category_name'] = self.category.name if self.category else None
        return data


# -------------------------------
# Payee Model
# -------------------------------

class Payee(db.Model):
    """
    Represents a payee entity for transactions.
    Attributes:
        id (int): Primary key.
        name (str): Payee name, unique and required.
        transactions (list): List of associated Transaction objects.
    """

    __tablename__ = 'payees'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)

    transactions = db.relationship('Transaction', back_populates='payee')

    def to_dict(self):
        """
        Converts the Payee object to a dictionary.
        Returns:
            dict: Dictionary with column names as keys and attribute values.
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# -------------------------------
# Transaction Model
# -------------------------------

class Transaction(db.Model):
    """
    Represents a financial transaction.
    Attributes:
        id (int): Primary key.
        date (date): Date of the transaction.
        amount (Decimal): Transaction amount.
        category_id (int): Foreign key to Category.
        account_id (int): Foreign key to Account.
        memo (str): Optional memo for the transaction.
        payee_id (int): Foreign key to Payee.
        category (Category): Relationship to Category.
        account (Account): Relationship to Account.
        payee (Payee): Relationship to Payee.
    """

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
        """
        Converts the Transaction object to a dictionary for JSON serialization.
        Returns:
            dict: Dictionary representation of the transaction.
        """
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
        """
        Deletes the transaction from the database.
        Returns:
            tuple: (success (bool), error_message (str or None))
        """
        try:
            db.session.delete(self)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)


# -------------------------------
# User Model
# -------------------------------

class User(db.Model):
    """
    Represents a user of the system.
    Attributes:
        id (int): Primary key.
        login (str): Unique login identifier.
        password (str): User password (hashed).
        active (bool): User activation status.
        email (str): Unique email address.
        name (str): User's full name.
    """
    __tablename__ = 'users'

    id = db.Column(db.BigInteger, primary_key=True)
    login = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    active = db.Column(db.Boolean, default=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    name = db.Column(db.Text, nullable=False)
