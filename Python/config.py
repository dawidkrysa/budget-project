import os

class Config:
    # If `SECRET_KEY` is not found in the environment variables, it falls back to the default value `"dev_secret"`
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev_secret")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.environ.get("FLASK_DEBUG", False)
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt_secret")