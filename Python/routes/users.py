#!/usr/bin/env python3
from flask import jsonify, request, redirect, url_for, make_response, Blueprint
from extensions import db
from .utils.db_utils import commit_session
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta, timezone
from config import Config

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
            return redirect(url_for('auth.login'))
        return error_response, status_code

    return jsonify({'message': 'Register successful'}), 200

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_login = request.form['login']
        password = request.form['password']
        user = User.query.filter_by(login=user_login).first()

        if not user or not check_password_hash(user.password, password):
            return jsonify({'message': 'Invalid login or password'}), 401

        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.now(timezone.utc) + timedelta(hours=1)},
                           Config.SECRET_KEY, algorithm="HS256")

        response = make_response(redirect(url_for('dashboard')))
        response.set_cookie('jwt_token', token)

        return response

    return jsonify({'message': 'Login successful'}), 200

