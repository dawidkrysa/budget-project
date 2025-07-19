from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)

    # Register blueprints
    # from app import auth_bp
    # from app import transaction_bp
    #
    # app.register_blueprint(auth_bp, url_prefix="/auth")
    # app.register_blueprint(transaction_bp, url_prefix="/transactions")

    return app