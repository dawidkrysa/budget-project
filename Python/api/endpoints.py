#!/usr/bin/env python3
from flask import Blueprint, jsonify, flash, redirect, url_for, request
from models.models import db, Transaction, Payee, Category, Account
from sqlalchemy import func
from web.views import web
from datetime import date

api = Blueprint('api', __name__, url_prefix='/api/v1')

@api.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "OK"})

@api.route("/transactions/<int:transaction_id>", methods=['PUT','DELETE'])
def update_transaction(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if transaction:
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

                transaction.date = data.get('date', transaction.date)
                transaction.account_id = data.get('account_id', transaction.account_id)
                transaction.category_id = data.get('category_id', transaction.category_id)
                transaction.payee_id = payee_id
                transaction.memo = data.get('memo', transaction.memo)
                transaction.amount = data.get('amount', transaction.amount)

                db.session.commit()
                return jsonify({"status": "success", "message": "Transaction updated."}), 200
            except Exception as e:
                db.session.rollback()
                return jsonify({"status": "error", "message": str(e)}), 500
        else:
            return jsonify({"status": "error", "message": "Invalid request."}), 400
    else:
        return jsonify({"status": "error", "message": "Transaction not found."}), 404

@api.route("/transactions", methods=['GET'])
def get_transactions():
    transactions_data = Transaction.query.all()
    return jsonify([t.to_dict() for t in transactions_data])

@api.route("/transactions", methods=['POST'])
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

@api.route('/transactions/form-data')
def transaction_form_data():
    categories = [ {'id': c.id, 'name': c.name} for c in Category.query.all() ]
    payees = [ {'id': p.id, 'name': p.name} for p in Payee.query.all() ]
    accounts = [ {'id': a.id, 'name': a.name} for a in Account.query.all() ]
    current_date = date.today().isoformat()
    return jsonify({
        'categories': categories,
        'payees': payees,
        'accounts': accounts,
        'date': current_date
    })

@api.route('/transactions/<int:transaction_id>/form-data')
def transaction_add_form_data(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    categories = [ {'id': c.id, 'name': c.name} for c in Category.query.all() ]
    payees = [ {'id': p.id, 'name': p.name} for p in Payee.query.all() ]
    accounts = [ {'id': a.id, 'name': a.name} for a in Account.query.all() ]
    return jsonify({
        'date': transaction.date.isoformat() if transaction.date else None,
        'account_id': transaction.account_id,
        'payee_name': transaction.payee.name,
        'category_id': transaction.category_id,
        'memo': transaction.memo,
        'amount': float(transaction.amount),  # convert decimal to float if needed
        'categories': categories,
        'payees': payees,
        'accounts': accounts,
    })

@api.route('/payees', methods=['GET','POST'])
def payees():
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
                # Add new payee
                new_payee = Payee(name=payee_name)
                db.session.add(new_payee)
                db.session.flush()  # Flush to get new_payee.id without committing
                db.session.commit()
                return jsonify(new_payee.to_dict()), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500
    return None


@api.route('/payees/<int:payee_id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
def payee(payee_id):
    payee = Payee.query.get(payee_id)
    if not payee:
        return jsonify({"status": "error", "message": "Payee not found."}), 404

    if request.method == 'GET':
        return jsonify(payee.to_dict()), 200

    elif request.method in ['PUT', 'PATCH']:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Invalid JSON body."}), 400

        # For PUT replace all fields, for PATCH update selectively
        # Payee has only 'name' attribute for simplicity

        if 'name' in data:
            payee.name = data['name']
        elif request.method == 'PUT':
            # PUT requires full replacement: if name missing, reject
            return jsonify({"status": "error", "message": "'name' is required for PUT."}), 400

        try:
            # Save changes
            db.session.commit()
            return jsonify(payee.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500

    elif request.method == 'DELETE':
        try:
            db.session.delete(payee)
            db.session.commit()
            return jsonify({"status": "success", "message": "Payee deleted."}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500
    return None