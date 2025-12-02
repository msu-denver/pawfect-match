"""
Application routes and views.

Author(s): Purple T-Pythons Team
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, login_manager
from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Home page route."""
    return render_template('index.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if request.method == 'POST':
        # TODO: Implement login logic

        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully!", "success")

            # Redirect to dashboard
            return redirect(url_for('main.dashboard'))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for('main.login'))

    return render_template('login.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if request.method == 'POST':
        # TODO: Implement registration logic

        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role') 

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for('main.register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered.", "danger")
            return redirect(url_for('main.register'))

        new_user = User(
            username=username,
            email=email,
            is_admin=(role == "admin")
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash("Account created successfully!", "success")

        if new_user.is_admin:
            return redirect(url_for('main.dashboard'))
        else:
            return redirect(url_for('main.dashboard'))

    return render_template('register.html')


@main.route('/logout')
@login_required
def logout():
    """User logout route."""
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@main.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing available pets."""
    # TODO: Query pets from database
    return render_template('dashboard.html')
