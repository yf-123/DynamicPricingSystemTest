from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///dynamic_pricing.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Import models and controllers
    from models import product, sales, pricing_history
    from controllers import product_controller, pricing_controller, analytics_controller

    # Register blueprints
    app.register_blueprint(product_controller.bp)
    app.register_blueprint(pricing_controller.bp)
    app.register_blueprint(analytics_controller.bp)

    @app.route('/')
    def index():
        return {'message': 'Dynamic Pricing System API', 'version': '1.0'}

    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}

    return app

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000) 