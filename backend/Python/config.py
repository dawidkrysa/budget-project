import os

class Config:
    # If `SECRET_KEY` is not found in the environment variables, it falls back to the default value `"dev_secret"`
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev_secret")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.environ.get("FLASK_DEBUG", False)
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt_secret")
    SWAGGER = {
        "specs_route": "/api/v1/docs/",
        'title': 'Home budget project API',
        'description': "Project documentation API",
        'swagger': '2.0',
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/api/v1/docs/apispec_1.json',
                "rule_filter": lambda rule: True,  # include all endpoints
                "model_filter": lambda tag: True,  # include all models
            }
        ]
    }