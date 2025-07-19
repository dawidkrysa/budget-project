#!/usr/bin/env python3
from flask import jsonify, request
from .api import api
from .utils.db_utils import commit_session
from models import Payee

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