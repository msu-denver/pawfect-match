"""
Flask application factory.

Author(s): Purple T-Pythons Team
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv

