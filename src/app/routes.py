"""
Application routes and views.

Author(s): Purple T-Pythons Team
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from src.app import db
from src.app.models import User

