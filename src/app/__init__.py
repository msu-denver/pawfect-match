"""
Flask application factory.

Author(s): Purple T-Pythons Team
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    """Create and configure the Flask application."""
    load_dotenv()
    
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///pawfect.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = True
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.index'
    
    # Register blueprints
    from src.app.routes import main
    app.register_blueprint(main)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    from src.app.models import User
    return User.query.get(int(user_id))

