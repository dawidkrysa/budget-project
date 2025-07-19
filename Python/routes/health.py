#!/usr/bin/env python3
from flask import jsonify
from Python import db
from .api import api


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