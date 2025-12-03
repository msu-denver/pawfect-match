"""
Database models for the application.

Author(s): Purple T-Pythons Team
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from datetime import datetime


class User(UserMixin, db.Model):
    """User model for authentication."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)


class Pet(db.Model):
    """Pet model for adoption listings."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(50), nullable=False)  # Dog or Cat
    breed = db.Column(db.String(100))
    age = db.Column(db.String(50))  # e.g., "1 year", "3 months"
    gender = db.Column(db.String(10))  # Male or Female
    spayed_neutered = db.Column(db.Boolean, default=False)
    vaccinated = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='available')  # available, pending, adopted
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Pet {self.name}>'
