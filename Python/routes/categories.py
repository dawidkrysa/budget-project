#!/usr/bin/env python3
from flask import jsonify, request, Blueprint
from .utils.db_utils import commit_session, token_required
from models import Category
from extensions import db

category_bp = Blueprint('categories', __name__)

# -------------------------------
# Categories Endpoints
# -------------------------------
@category_bp.route('', methods=['GET','POST'])
@token_required
def get_categories(current_user, budget_id):
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

@category_bp.route('/<string:category_id>', methods=['PATCH'])
@token_required
def update_category(current_user, budget_id, category_id):
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
