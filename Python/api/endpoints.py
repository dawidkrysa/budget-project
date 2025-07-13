#!/usr/bin/env python3
from flask import Blueprint, jsonify, request
from models.models import db, Transaction, Payee, Category, Account, Budget, CategoryName, Month
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, DataError, OperationalError, ProgrammingError, StatementError, InvalidRequestError, DBAPIError
from datetime import date, datetime
import sys
api = Blueprint('api', __name__, url_prefix='/api/v1/budgets/<string:budget_id>')

# -------------------------------
# Health Check Endpoint
# -------------------------------

@api.route('/status', methods=['GET'])
def status():
    """
    Endpoint to check API and database status.
    Returns:
        JSON with status "OK" if API and DB are healthy, otherwise "ERROR"
    """
    db_status = "OK"
    try:
        # A very lightweight query to check database connectivity
        db.session.execute('SELECT 1')
    except Exception as e:
        db_status = f"ERROR: {str(e)}"

    return jsonify({
        "status": "OK",
        "database": db_status
    })


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

# -------------------------------
# Transaction Endpoints
# -------------------------------

@api.route("/transactions/<string:transaction_id>", methods=['PUT', 'DELETE'])
def update_transaction(budget_id, transaction_id):
    """
    Update or delete a transaction by ID.
    PUT: Update transaction fields including dynamic payee creation.
    DELETE: Delete transaction by ID.
    """
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({"status": "error", "message": "Transaction not found."}), 404

    if request.method == 'DELETE':
        transaction.deleted = True
        success, error_response, status_code=commit_session()
        if success:
            return jsonify({"status": "success", "message": "Transaction deleted."}), 200
        else:
            return jsonify({"status": "error", "message": error_response}), 500

    elif request.method == 'PUT':
        data = request.get_json()
        payee_name = data.get('payee_name')
        if not payee_name:
            return jsonify({"status": "error", "message": "Payee name is required."}), 400

        payee, _ = get_payee(budget_id, payee_name)
        category, _ = get_category_month(budget_id, data['category_id'], datetime.strptime(data['date'], "%Y-%m-%d").date())


        # Update transaction fields
        transaction.date = data.get('date', transaction.date)
        transaction.account_id = data.get('account_id', transaction.account_id)
        transaction.category_id = data.get(category.id, transaction.category_id)
        transaction.payee_id = payee.id
        transaction.memo = data.get('memo', transaction.memo)
        transaction.amount = data.get('amount', transaction.amount)

        success, error_response, status_code = commit_session()
        if success:
            return jsonify({"status": "success", "message": "Transaction updated."}), 200
        else:
            return error_response, status_code

    else:
        return jsonify({"status": "error", "message": "Invalid request."}), 400


@api.route("/transactions", methods=['GET'])
def get_transactions(budget_id):
    """
    Retrieve all transactions.
    Returns:
        JSON list of all transactions as dictionaries.
    """
    transactions_data = Transaction.query.filter(Transaction.budget_id == budget_id).all()
    return jsonify([t.to_dict() for t in transactions_data])


@api.route("/transactions", methods=['POST'])
def add_transaction(budget_id):
    """
    Add a new transaction.
    Expects JSON body with required fields including 'payee_name'.
    """
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Invalid request."}), 400

    payee_name = data.get('payee_name')
    if not payee_name:
        return jsonify({"status": "error", "message": "Payee name is required."}), 400

    payee, _ = get_payee(budget_id, payee_name)
    category, _ = get_category_month(budget_id, data['category_id'], datetime.strptime(data['date'], "%Y-%m-%d").date())

    transaction = Transaction(
        date=data['date'],
        account_id=data['account_id'],
        payee_id=payee.id,
        category_id=category.id,
        amount=data['amount'],
        memo=data.get('memo'),
        budget_id = budget_id
    )

    db.session.add(transaction)
    success, error_response, status_code = commit_session()
    # print(success, file=sys.stderr)
    if success:
        return jsonify(transaction.to_dict()), 200
    else:
        return error_response, status_code



@api.route('/transactions/form-data')
def transaction_form_data(budget_id):
    """
    Get supporting data needed for transaction form.
    Returns:
        JSON including categories, payees, accounts, and current date.
    """
    categories, payees, accounts = get_form_data(budget_id)
    current_date = date.today().isoformat()
    return jsonify({
        'categories': categories,
        'payees': payees,
        'accounts': accounts,
        'date': current_date
    })


@api.route('/transactions/<string:transaction_id>/form-data')
def transaction_add_form_data(budget_id, transaction_id):
    """
    Get data and form defaults for editing a specific transaction.
    Returns:
        JSON with transaction data plus categories, payees, and accounts.
    """
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({"status": "error", "message": "Transaction not found."}), 404

    categories, payees, accounts = get_form_data(budget_id)

    return jsonify({
        'date': transaction.date.isoformat() if transaction.date else None,
        'account_id': transaction.account_id,
        'payee_name': transaction.payee.name,
        'category_id': transaction.category.category_name.id,
        'memo': transaction.memo,
        'amount': float(transaction.amount),
        'categories': categories,
        'payees': payees,
        'accounts': accounts,
    })


# -------------------------------
# Payee Endpoints
# -------------------------------

@api.route('/payees', methods=['GET', 'POST'])
def manage_payees(budget_id):
    """
    GET: List all payees.
    POST: Add a new payee.
    """
    if request.method == 'GET':
        payee_data = Payee.query.filter(Payee.budget_id == budget_id).all()
        return jsonify([p.to_dict() for p in payee_data]), 200

    elif request.method == 'POST':
        if request.is_json:
            payee_name = request.get_json().get('name')
        else:
            payee_name = request.form.get('name')
        if not payee_name:
            return jsonify({"status": "error", "message": "Payee name is required."}), 400

        existing_payee = db.session.query(Payee).filter(
            func.lower(Payee.name) == payee_name.lower()
        ).filter(Payee.budget_id == budget_id).first()

        if existing_payee:
            return jsonify({"status": "error", "message": "Payee name already exists."}), 403
        else:
            new_payee = Payee(name=payee_name, budget_id=budget_id)
            db.session.add(new_payee)
            success, error_response, status_code = commit_session()
            if success:
                return jsonify(new_payee.to_dict()), 200
            else:
                return error_response, status_code


    return jsonify({"status": "error", "message": "Method not allowed."}), 405


@api.route('/payees/<string:payee_id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
def manage_payee(budget_id, payee_id):
    """
    Manage a specific payee by ID.
    GET: Retrieve payee info.
    PUT/PATCH: Update payee name.
    DELETE: Remove payee.
    """
    payee = Payee.query.get(payee_id)
    if not payee:
        return jsonify({"status": "error", "message": "Payee not found."}), 404

    if request.method == 'GET':
        return jsonify(payee.to_dict()), 200

    elif request.method in ['PUT', 'PATCH']:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Invalid JSON body."}), 400

        if 'name' in data:
            payee.name = data['name']
        elif request.method == 'PUT':
            # PUT requires full replacement; 'name' missing means error
            return jsonify({"status": "error", "message": "'name' is required for PUT."}), 400

        success, error_response, status_code = commit_session()
        if success:
            return jsonify(payee.to_dict()), 200
        else:
            return error_response, status_code

    elif request.method == 'DELETE':
        payee.deleted = True
        success, error_response, status_code = commit_session()
        if success:
            return jsonify({"status": "success", "message": "Payee deleted."}), 200
        else:
            return error_response, status_code

    return jsonify({"status": "error", "message": "Method not allowed."}), 405

# -------------------------------
# Categories Endpoints
# -------------------------------
@api.route('/categories', methods=['GET','POST'])
def get_categories(budget_id):
    """
    Get all categories.
    GET: Retrieve categories list.
    """
    if request.method == 'GET':
        # Get category if it's provided
        category = request.args.get("category_name")

        query = Category.query.filter_by(name=category, budget_id=budget_id)

        if category:
            query =  query.filter(Category.name.ilike(f"%{category}%"))

        category = query.all()
        return jsonify([c.to_dict() for c in category]), 200

    elif request.method == 'POST':
        if request.is_json:
            new_category = Category()
            new_category.name = request.form.get("category_name")
            new_category.category_group_id = request.form.get("category_group_id")
            new_category.budget_id = budget_id

            db.session.add(new_category)
            success, error_response, status_code = commit_session()
            if success:
                return jsonify(new_category.to_dict()), 200
            else:
                return error_response, status_code

    return jsonify({"status": "error", "message": "Method not allowed."}), 405

@api.route('/categories/<string:category_id>', methods=['PATCH'])
def update_category(budget_id, category_id):
    """
    PATCH /categories/<category_id>
    Partially update the category's assigned amount.
    JSON body must include: { "assigned": <number> }
    """
    category = Category.query.get(category_id)
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON body."}), 400

    if not category:
        return jsonify({"status": "error", "message": "Category not found."}), 404

    if 'assigned' not in data:
        return jsonify({"status": "error", "message": "'assigned' is required for PATCH."}), 400

    # Optional: validate assigned is a number
    try:
        assigned_value = float(data['assigned'])
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "'assigned' must be a number."}), 400

    category.budgeted = assigned_value

    success, error_response, status_code = commit_session()
    if success:
        return jsonify(category.to_dict()), 200
    else:
        return error_response, status_code
