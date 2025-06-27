from flask import Blueprint, jsonify

api = Blueprint('api', __name__, url_prefix='/api/v1/')

@api.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "OK"})