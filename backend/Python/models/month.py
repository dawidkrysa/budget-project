#!/usr/bin/env python3
from models.base import BaseModel, db, uuid4, UUID

# -------------------------------
# Month Model
# -------------------------------

class Month(BaseModel):
    """
    Represents a month for budgeting.
    """
    __tablename__ = 'months'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    month = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, primary_key=True)
    budgeted = db.Column(db.Numeric(15, 2), default=0)
    activity = db.Column(db.Numeric(15, 2), default=0)
    to_be_budgeted = db.Column(db.Numeric(15, 2), default=0)
    deleted = db.Column(db.Boolean, default=False)
    budget_id = db.Column(db.String(36), db.ForeignKey('budgets.id'), nullable=False)

    categories = db.relationship('Category', back_populates='month')