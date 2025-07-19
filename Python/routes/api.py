#!/usr/bin/env python3
from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='/api/v1/budgets/<string:budget_id>')
