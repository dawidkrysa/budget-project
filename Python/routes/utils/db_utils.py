#!/usr/bin/env python3
from Python import db
from models import Month, Category, Payee
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, DataError, OperationalError, ProgrammingError, StatementError, InvalidRequestError, DBAPIError
from datetime import date

# -------------------------------
# Helper Functions
# -------------------------------
def get_payee(budget_id, payee_name: str):
    """
    Return an existing Payee by case-insensitive name, or create a new one.
    """
    existing_payee = db.session.query(Payee).filter(
        func.lower(Payee.name) == payee_name.lower()
    ).filter(Payee.budget_id == budget_id).first()
    if existing_payee:
        return existing_payee, False
    new_payee = Payee(name=payee_name)
    db.session.add(new_payee)
    db.session.flush()  # Get ID without committing
    return new_payee, True

def get_category_month(budget_id, category_name_id: str, transaction_date: date):
    """
    Return an existing Category.
    """
    month = (
        Month.query
        .filter_by(budget_id=budget_id, month=transaction_date.month, year=transaction_date.year)
        .first()
    )
    if not month:
        month = Month(
            month=transaction_date.month,
            year=transaction_date.year,
            budgeted=0,
            activity=0,
            to_be_budgeted=0,
            deleted=False,
            budget_id=budget_id
        )
        db.session.add(month)
        db.session.flush()  # gets month.id

    category = (
        Category.query
        .filter_by(
            budget_id=budget_id,
            category_name_id=category_name_id,
            month_id=month.id
        )
        .first()
    )

    if category:
        return category, False

    return category, True


def get_form_data(budget_id):
    """
    Retrieve form data for transactions: categories, payees, accounts.
    """
    categories = [{'id': c.id, 'name': c.name} for c in CategoryName.query.all()]
    payees = [{'id': p.id, 'name': p.name} for p in Payee.query.filter_by(
        budget_id= budget_id,
        deleted= False
    ).all()]
    accounts = [{'id': a.id, 'name': a.name} for a in Account.query.filter_by(
        budget_id= budget_id,
        deleted= False
    ).all()]
    return categories, payees, accounts


def commit_session():
    """
    Commit the current DB session, rollback if error occurs.
    Return (success: bool, error_message: Optional[str], status code: integer)
    """
    try:
        db.session.commit()
        return True, None, 200
    except IntegrityError as e:
        db.session.rollback()
        return False, jsonify({
            "status": "error",
            "message": "A database constraint was violated. Likely a duplicate or foreign key issue.",
        }), 400
    except DataError as e:
        db.session.rollback()
        return False, jsonify({
            "status": "error",
            "type": "DataError",
            "message": "Invalid data format or out-of-range value.",
            # "details": str(e.orig)
        }), 400
    except OperationalError as e:
        db.session.rollback()
        return False, jsonify({
            "status": "error",
            "type": "OperationalError",
            "message": "Database operational error. This could be a lost connection or misconfiguration.",
        }), 500
    except ProgrammingError as e:
        db.session.rollback()
        return False, jsonify({
            "status": "error",
            "type": "ProgrammingError",
            "message": "There was a database programming error, such as a malformed SQL statement.",
        }), 500
    except DBAPIError as e:
        db.session.rollback()
        return False, jsonify({
            "status": "error",
            "type": "DBAPIError",
            "message": "Low-level database driver error.",
        }), 500
    except StatementError as e:
        db.session.rollback()
        return False, jsonify({
            "status": "error",
            "type": "StatementError",
            "message": "There was an error preparing or executing the database statement.",
            # "details": str(e.orig)
        }), 400
    except InvalidRequestError as e:
        db.session.rollback()
        return False, jsonify({
            "status": "error",
            "type": "InvalidRequestError",
            "message": "Invalid request to the database session or improper use of the ORM.",
        }), 400
    except Exception as e:
        db.session.rollback()
        return False, jsonify({
            "status": "error",
            "type": "UnknownError",
            "message": "An unexpected error occurred while saving to the database.",
        }), 500