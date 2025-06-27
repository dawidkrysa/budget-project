from flask import Flask
from web.views import web
from api.endpoints import api

app = Flask(__name__)
app.register_blueprint(web)
app.register_blueprint(api)