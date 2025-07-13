#!/usr/bin/env python3
from flask import Blueprint, jsonify, request
from models.models import db, Transaction, Payee, Category, Account, Budget
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, DataError, OperationalError, ProgrammingError, StatementError, InvalidRequestError, DBAPIError
from datetime import date

api = Blueprint('api', __name__, url_prefix='/api/v1')


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
def get_payee(payee_name: str):
    """
    Return an existing Payee by case-insensitive name, or create a new one.
    """
    existing_payee = db.session.query(Payee).filter(
        func.lower(Payee.name) == payee_name.lower()
    ).first()
    if existing_payee:
        return existing_payee, False
    new_payee = Payee(name=payee_name)
    db.session.add(new_payee)
    db.session.flush()  # Get ID without committing
    return new_payee, True


def get_form_data():
    """
    Retrieve form data for transactions: categories, payees, accounts.
    """
    categories = [{'id': c.id, 'name': c.name} for c in Category.query.filter(Category.main_category_id.isnot(None)).all()]
    payees = [{'id': p.id, 'name': p.name} for p in Payee.query.all()]
    accounts = [{'id': a.id, 'name': a.name} for a in Account.query.all()]
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

@api.route("/transactions/<int:transaction_id>", methods=['PUT', 'DELETE'])
def update_transaction(transaction_id):
    """
    Update or delete a transaction by ID.
    PUT: Update transaction fields including dynamic payee creation.
    DELETE: Delete transaction by ID.
    """
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({"status": "error", "message": "Transaction not found."}), 404

    if request.method == 'DELETE':
        success, error = transaction.delete()
        if success:
            return jsonify({"status": "success", "message": "Transaction deleted."}), 200
        else:
            return jsonify({"status": "error", "message": error}), 500

    elif request.method == 'PUT':
        data = request.get_json()
        payee_name = data.get('payee_name')
        if not payee_name:
            return jsonify({"status": "error", "message": "Payee name is required."}), 400

        payee, _ = get_payee(payee_name)

        # Update transaction fields
        transaction.date = data.get('date', transaction.date)
        transaction.account_id = data.get('account_id', transaction.account_id)
        transaction.category_id = data.get('category_id', transaction.category_id)
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
def get_transactions():
    """
    Retrieve all transactions.
    Returns:
        JSON list of all transactions as dictionaries.
    """
    transactions_data = Transaction.query.all()
    return jsonify([t.to_dict() for t in transactions_data])


@api.route("/transactions", methods=['POST'])
def add_transaction():
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

    payee, _ = get_payee(payee_name)

    transaction = Transaction(
        date=data['date'],
        account_id=data['account_id'],
        payee_id=payee.id,
        category_id=data['category_id'],
        amount=data['amount'],
        memo=data.get('memo'),
    )

    db.session.add(transaction)
    success, error_response, status_code = commit_session()
    if success:
        return jsonify(transaction.to_dict()), 200
    else:
        return error_response, status_code



@api.route('/transactions/form-data')
def transaction_form_data():
    """
    Get supporting data needed for transaction form.
    Returns:
        JSON including categories, payees, accounts, and current date.
    """
    categories, payees, accounts = get_form_data()
    current_date = date.today().isoformat()
    return jsonify({
        'categories': categories,
        'payees': payees,
        'accounts': accounts,
        'date': current_date
    })


@api.route('/transactions/<int:transaction_id>/form-data')
def transaction_add_form_data(transaction_id):
    """
    Get data and form defaults for editing a specific transaction.
    Returns:
        JSON with transaction data plus categories, payees, and accounts.
    """
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({"status": "error", "message": "Transaction not found."}), 404

    categories, payees, accounts = get_form_data()

    return jsonify({
        'date': transaction.date.isoformat() if transaction.date else None,
        'account_id': transaction.account_id,
        'payee_name': transaction.payee.name,
        'category_id': transaction.category_id,
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
def manage_payees():
    """
    GET: List all payees.
    POST: Add a new payee.
    """
    if request.method == 'GET':
        payee_data = Payee.query.all()
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
        ).first()

        if existing_payee:
            return jsonify({"status": "error", "message": "Payee name already exists."}), 403
        else:
            new_payee = Payee(name=payee_name)
            db.session.add(new_payee)
            success, error_response, status_code = commit_session()
            if success:
                return jsonify(new_payee.to_dict()), 200
            else:
                return error_response, status_code


    return jsonify({"status": "error", "message": "Method not allowed."}), 405


@api.route('/payees/<int:payee_id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
def manage_payee(payee_id):
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

        db.session.delete(payee)
        success, error_response, status_code = commit_session()
        if success:
            return jsonify({"status": "success", "message": "Payee deleted."}), 200
        else:
            return error_response, status_code

    return jsonify({"status": "error", "message": "Method not allowed."}), 405

# -------------------------------
# Budget Endpoints
# -------------------------------

@api.route('/budgets', methods=['GET','POST'])
def get_budgets():
    """
    Get all budgets.
    GET: Retrieve budget list.
    """
    if request.method == 'GET':
        # Get category if it's provided
        category = request.args.get("category_name")
        year = request.args.get("year")
        month = request.args.get("month")

        query = Budget.query.join(Budget.category)

        if category:
            query =  query.filter(Category.name.ilike(f"%{category}%")) \
                .filter(Category.main_category_id.isnot(None))

        try:
            year = int(year) if year else None
            month = int(month) if month else None
        except ValueError:
            return jsonify({"status": "error", "message": "Year and month must be integers."}), 400

        if year is not None:
            query = query.filter(Budget.year == year)

        if month is not None:
            query = query.filter(Budget.month == month)

        budgets = query.all()
        return jsonify([b.to_dict() for b in budgets]), 200

    elif request.method == 'POST':
        if request.is_json:
            new_budget = Budget()
            new_budget.assigned = request.get_json().get('assigned')
            new_budget.year = request.get_json().get('year')
            new_budget.month = request.get_json().get('month')
            new_budget.category_id = request.get_json().get('category_id')

            db.session.add(new_budget)
            success, error_response, status_code = commit_session()
            if success:
                return jsonify(new_budget.to_dict()), 200
            else:
                return error_response, status_code

    return jsonify({"status": "error", "message": "Method not allowed."}), 405

@api.route('/budgets/<int:budget_id>', methods=['PATCH'])
def update_budget(budget_id):
    """
    PATCH /budgets/<budget_id>
    Partially update the budget's assigned amount.
    JSON body must include: { "assigned": <number> }
    """
    budget = Budget.query.get(budget_id)
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON body."}), 400

    if not budget:
        return jsonify({"status": "error", "message": "Budget not found."}), 404

    if 'assigned' not in data:
        return jsonify({"status": "error", "message": "'assigned' is required for PATCH."}), 400

    # Optional: validate assigned is a number
    try:
        assigned_value = float(data['assigned'])
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "'assigned' must be a number."}), 400

    budget.assigned = assigned_value

    success, error_response, status_code = commit_session()
    if success:
        return jsonify(budget.to_dict()), 200
    else:
        return error_response, status_code
