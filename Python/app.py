#!/usr/bin/env python3
from flask import Flask
from extensions.database import db
from web.views import web
from api.endpoints import api
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db/{os.getenv('POSTGRES_DB')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('FLASK_SECRET_KEY')

db.init_app(app)

app.register_blueprint(web)
app.register_blueprint(api)

with app.app_context():
    db.create_all()
