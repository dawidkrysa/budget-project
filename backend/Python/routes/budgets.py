from flask import jsonify, request, Blueprint
from .utils.db_utils import commit_session, token_required
from models import Budget
from extensions import db

budget_bp = Blueprint('budgets', __name__)


# -------------------------------
# Categories Endpoints
# -------------------------------
@budget_bp.route('', methods=['GET'])
@token_required
def get_budgets(current_user):
    budgets = Budget.query.all()
    return jsonify([b.to_dict() for b in budgets]), 200