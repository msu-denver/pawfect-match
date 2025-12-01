"""
Database models for the application.

Author(s): Purple T-Pythons Team
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from src.app import db


