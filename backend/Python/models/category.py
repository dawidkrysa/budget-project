#!/usr/bin/env python3
from models.base import BaseModel, db, uuid4, UUID

# -------------------------------
# Category Model
# -------------------------------

class Category(BaseModel):
    """
    Represents a transaction category for a specific month.
    """
    __tablename__ = 'categories'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
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

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
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

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = db.Column(db.Text, nullable=False, unique=True)
    deleted = db.Column(db.Boolean, default=False)
    budget_id = db.Column(db.String(36), db.ForeignKey('budgets.id'), nullable=False)

    categories = db.relationship('Category', back_populates='category_group')