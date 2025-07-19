from models.base import BaseModel, db, uuid

# -------------------------------
# Account Model
# -------------------------------
class Account(BaseModel):
    """
    Represents a financial account.
    """
    __tablename__ = 'accounts'

    id = db.Column(db.UUID, primary_key=True, default=lambda: str(uuid.uuid4()))  # UUID string
    name = db.Column(db.Text, nullable=False, unique=True)
    type_id = db.Column(db.String(36), db.ForeignKey('accountsType.id'), nullable=True)
    deleted = db.Column(db.Boolean, default=False)
    balance = db.Column(db.Numeric(15, 2), nullable=True)
    transfer_payee_id = db.Column(db.String(36), nullable=True)  # Should be a UUID too
    budget_id = db.Column(db.String(36), db.ForeignKey('budgets.id'), nullable=False)

    accountsType = db.relationship('AccountsType', back_populates='accounts')
    transactions = db.relationship('Transaction', back_populates='account')


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

    accounts = db.relationship('Account', back_populates='accountsType')