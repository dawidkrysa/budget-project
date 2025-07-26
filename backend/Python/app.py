#!/usr/bin/env python3
from flask import jsonify
from flask import Flask
from dotenv import load_dotenv
from extensions import db, migrate, jwt, cors
from routes import user_bp, transaction_bp, category_bp, payee_bp, health_bp
from flasgger import Swagger

load_dotenv()
app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize extensions
db.init_app(app)
migrate.init_app(app, db)
jwt.init_app(app)
cors.init_app(app)
# Create swagger documentation
swagger = Swagger(app, template_file='swagger/swagger.yml')

# Register blueprints
main_prefix = '/api/v1'
budget_prefix = '/budgets/<uuid:budget_id>'

app.register_blueprint(user_bp, url_prefix=main_prefix + '/auth')
app.register_blueprint(transaction_bp, url_prefix=main_prefix + budget_prefix + '/transactions')
app.register_blueprint(category_bp, url_prefix=main_prefix + budget_prefix + '/categories')
app.register_blueprint(payee_bp, url_prefix=main_prefix + budget_prefix + '/payees')
app.register_blueprint(health_bp, url_prefix=main_prefix + '/health')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)

@app.route('/api/v1/routes', methods=['GET'])
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(str(rule.rule))
    return jsonify(routes)
