#!/usr/bin/env python3
from flask import jsonify, Blueprint
from extensions import db

health_bp = Blueprint('health', __name__)
# -------------------------------
# Health Check Endpoint
# -------------------------------

@health_bp.route('/status', methods=['GET'])
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