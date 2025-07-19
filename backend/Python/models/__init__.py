"""
Database models initialization module.

This module initializes and exports all database models used in the application.
It provides a central point for importing models and manages their dependencies.

Note: Import models only when needed to avoid circular dependencies.
"""
from typing import List

# Base model import
from .base import BaseModel

# Domain models in alphabetical order
from .account import Account, AccountsType
from .budget import Budget
from .category import (
    Category,
    CategoryName,
    CategoryGroup,
)
from .month import Month
from .payee import Payee
from .transaction import Transaction
from .user import User

# Define exported symbols
__all__: List[str] = [
    # Base
    'BaseModel',

    # Account related
    'Account',
    'AccountsType',

    # Budget
    'Budget',

    # Category related
    'Category',
    'CategoryName',
    'CategoryGroup',

    # Other models
    'Month',
    'Payee',
    'Transaction',
    'User',
]

# Prevent circular imports by defining relationships after all models are loaded
def _setup_relationships() -> None:
    """Initialize model relationships to prevent circular dependencies."""
    pass

# Setup relationships when module is imported
_setup_relationships()
