#!/usr/bin/env python3
from flask import jsonify, request, Blueprint
from .utils.db_utils import commit_session, get_payee, get_category_month, get_form_data, token_required
from models import Transaction
from extensions import db
from datetime import datetime, date


transaction_bp = Blueprint('transactions', __name__)
# -------------------------------
# Transaction Endpoints
# -------------------------------

@transaction_bp.route("/<string:transaction_id>", methods=['PUT', 'DELETE'])
@token_required
def update_transaction(current_user, budget_id, transaction_id):
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
        transaction.category_id = category.id
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


@transaction_bp.route("", methods=['GET'])
@token_required
def get_transactions(current_user, budget_id):
    """
    Retrieve all transactions, optionally expanding related entities.
    """
    expand_fields = request.args.get('expand', '')  # e.g., "account,category"
    expand_fields = [e.strip() for e in expand_fields.split(',') if e.strip()]

    transactions_data = Transaction.query.filter(Transaction.budget_id == budget_id).all()
    return jsonify([t.to_dict(expand=expand_fields) for t in transactions_data])


@transaction_bp.route("", methods=['POST'])
@token_required
def add_transaction(current_user, budget_id):
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



@transaction_bp.route('/form-data')
@token_required
def transaction_form_data(current_user, budget_id):
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


@transaction_bp.route('/<string:transaction_id>/form-data')
@token_required
def transaction_add_form_data(current_user, budget_id, transaction_id):
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
