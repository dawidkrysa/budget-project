#!/usr/bin/env python3
from flask import Blueprint, jsonify, flash, redirect, url_for, request
from models.models import db, Transaction, Payee, Category, Account
from sqlalchemy import func
from web.views import web

api = Blueprint('api', __name__, url_prefix='/api/v1')

@api.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "OK"})

@api.route("/delete/<int:transaction_id>", methods=['POST'])
def delete(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if transaction:
        try:
            db.session.delete(transaction)
            db.session.commit()
            db.session.close()
            return jsonify({"status": "success", "message": "Transaction deleted."}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "Transaction not found."}), 404

@api.route("/transactions", methods=['GET'])
def get_transactions():
    transactions_data = Transaction.query.all()
    return jsonify([t.to_dict() for t in transactions_data])

@api.route("/transactions/add", methods=['POST'])
def add_transaction():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Invalid request."}), 400

    payee_name = data.get('payee_name')
    if not payee_name:
        return jsonify({"status": "error", "message": "Payee name is required."}), 400

    try:
        # Case-insensitive search for existing payee
        existing_payee = db.session.query(Payee).filter(
            func.lower(Payee.name) == payee_name.lower()
        ).first()

        if existing_payee:
            payee_id = existing_payee.id
        else:
            # Add new payee
            new_payee = Payee(name=payee_name)
            db.session.add(new_payee)
            db.session.flush()  # Flush to get new_payee.id without committing
            payee_id = new_payee.id

        # Create the transaction with correct payee_id
        transaction = Transaction(
            date=data['date'],
            account_id=data['account_id'],
            payee_id=payee_id,
            category_id=data['category_id'],
            amount=data['amount'],
            memo=data['memo'],
        )

        db.session.add(transaction)
        db.session.commit()

        return jsonify(transaction.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@api.route('/transaction_form_data')
def transaction_form_data():
    categories = [ {'id': c.id, 'name': c.name} for c in Category.query.all() ]
    payees = [ {'id': p.id, 'name': p.name} for p in Payee.query.all() ]
    accounts = [ {'id': a.id, 'name': a.name} for a in Account.query.all() ]
    return jsonify({
        'categories': categories,
        'payees': payees,
        'accounts': accounts
    })

@web.route("/transactions/delete/<int:transaction_id>")
def delete_transaction(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if transaction:
        try:
            db.session.delete(transaction)
            db.session.commit()
            flash("Transaction deleted.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error deleting transaction: {str(e)}", "error")
    else:
        flash("Transaction not found.", "error")
    return redirect(url_for("web.transactions"))