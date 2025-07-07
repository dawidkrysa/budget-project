#!/usr/bin/env python3
from flask import Blueprint, jsonify, request
from models.models import db, Transaction, Payee, Category, Account
from sqlalchemy import func
from datetime import date

api = Blueprint('api', __name__, url_prefix='/api/v1')


# -------------------------------
# Health Check Endpoint
# -------------------------------

@api.route('/status', methods=['GET'])
def status():
    """
    Simple endpoint to check API status.
    Returns:
        JSON with status "OK"
    """
    return jsonify({"status": "OK"})



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
    categories = [{'id': c.id, 'name': c.name} for c in Category.query.filter(Category.main_category_id != None).all()]
    payees = [{'id': p.id, 'name': p.name} for p in Payee.query.all()]
    accounts = [{'id': a.id, 'name': a.name} for a in Account.query.all()]
    return categories, payees, accounts


def commit_session():
    """
    Commit the current DB session, rollback if error occurs.
    Return (success: bool, error_message: Optional[str])
    """
    try:
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        return False, str(e)

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

        try:
            payee, _ = get_payee(payee_name)

            # Update transaction fields
            transaction.date = data.get('date', transaction.date)
            transaction.account_id = data.get('account_id', transaction.account_id)
            transaction.category_id = data.get('category_id', transaction.category_id)
            transaction.payee_id = payee.id
            transaction.memo = data.get('memo', transaction.memo)
            transaction.amount = data.get('amount', transaction.amount)

            success, error = commit_session()
            if success:
                return jsonify({"status": "success", "message": "Transaction updated."}), 200
            else:
                return jsonify({"status": "error", "message": error}), 500

        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500

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

    try:
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
        success, error = commit_session()
        if success:
            return jsonify(transaction.to_dict()), 200
        else:
            return jsonify({"status": "error", "message": error}), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


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
def payees():
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
        try:
            existing_payee = db.session.query(Payee).filter(
                func.lower(Payee.name) == payee_name.lower()
            ).first()

            if existing_payee:
                return jsonify({"status": "error", "message": "Payee name already exists."}), 403
            else:
                new_payee = Payee(name=payee_name)
                db.session.add(new_payee)
                success, error = commit_session()
                if success:
                    return jsonify(new_payee.to_dict()), 200
                else:
                    return jsonify({"status": "error", "message": error}), 500

        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500

    return None


@api.route('/payees/<int:payee_id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
def payee(payee_id):
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

        success, error = commit_session()
        if success:
            return jsonify(payee.to_dict()), 200
        else:
            return jsonify({"status": "error", "message": error}), 500

    elif request.method == 'DELETE':
        try:
            db.session.delete(payee)
            success, error = commit_session()
            if success:
                return jsonify({"status": "success", "message": "Payee deleted."}), 200
            else:
                return jsonify({"status": "error", "message": error}), 500
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500

    return None
