#!/usr/bin/env python3
import sys

from flask import jsonify, request, redirect, url_for, make_response, Blueprint
from extensions import db
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta, timezone
from config import Config
from .utils.db_utils import commit_session, token_required


user_bp = Blueprint('auth', __name__)

@user_bp.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_login = request.form['login']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Validate required fields
        if not all([user_login, name, email, password]):
            return jsonify({'message': 'All fields are required'}), 400

        # Basic input validation
        if len(password) < 8:
            return jsonify({'message': 'Password must be at least 8 characters long'}), 400

        # Check existing user/email
        if User.query.filter_by(login=user_login).first():
            return jsonify({'message': 'Username already exists'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already registered'}), 400

        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(
            name=name.strip(),
            email=email.lower().strip(),
            password=hashed_password,
            active=True,
            login=user_login.strip()
        )

        db.session.add(new_user)
        success, error_response, status_code = commit_session()

        if success:
            return login(user_login, password)
        return error_response, status_code

    return jsonify({'message': 'Register successful'}), 200

@user_bp.route('/login', methods=['POST','GET'])
def login(in_login=None,in_password=None):
    if request.method == 'POST':
        user_login = request.form['login'] if in_login is None else in_login
        password = request.form['password'] if in_password is None else in_password
        user = User.query.filter_by(login=user_login).first()

        if not user or not check_password_hash(user.password, password):
            return jsonify({'message': 'Invalid login or password'}), 401

        token = jwt.encode({'user_id': str(user.id), 'exp': datetime.now(timezone.utc) + timedelta(hours=1)},
                           Config.SECRET_KEY, algorithm="HS256")

        response = jsonify({'status': 'ok', 'message': 'Login successful'})
        response.set_cookie('access_token', token, httponly=False, samesite='strict', secure=True,
                            expires=datetime.now(timezone.utc) + timedelta(hours=1))

        return response

    return jsonify({'message': 'Send a POST request to login'}), 200

