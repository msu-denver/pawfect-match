"""
Application routes and views.

Author(s): Purple T-Pythons Team
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from src.app import db
from src.app.models import User, Pet

main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Home page showing available pets."""
    pets = Pet.query.filter_by(status='available').all()
    return render_template('index.html', pets=pets)


@main.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for('main.dashboard'))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for('main.login'))

    return render_template('login.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if request.method == 'POST':
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
    """Dashboard showing different views for admin vs adopter."""
    pets = Pet.query.all()
    if current_user.is_admin:
        return render_template('admin_dashboard.html', pets=pets)
    else:
        pets = Pet.query.filter_by(status='available').all()
        return render_template('adopter_dashboard.html', pets=pets)


@main.route('/pet/add', methods=['GET', 'POST'])
@login_required
def add_pet():
    """Add a new pet (admin only)."""
    if not current_user.is_admin:
        flash('Only admins can add pets.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        pet = Pet(
            name=request.form.get('name'),
            species=request.form.get('species'),
            breed=request.form.get('breed'),
            age=request.form.get('age', type=int),
            gender=request.form.get('gender'),
            spayed_neutered=request.form.get('spayed_neutered') == 'on',
            vaccinated=request.form.get('vaccinated') == 'on',
            description=request.form.get('description'),
            image_url=request.form.get('image_url')
        )
        db.session.add(pet)
        db.session.commit()
        flash(f'Pet {pet.name} added successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('add_pet.html')


@main.route('/pet/<int:pet_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_pet(pet_id):
    """Edit pet details (admin only)."""
    if not current_user.is_admin:
        flash('Only admins can edit pets.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    pet = Pet.query.get_or_404(pet_id)
    
    if request.method == 'POST':
        pet.name = request.form.get('name')
        pet.species = request.form.get('species')
        pet.breed = request.form.get('breed')
        pet.age = request.form.get('age', type=int)
        pet.description = request.form.get('description')
        pet.status = request.form.get('status')
        pet.image_url = request.form.get('image_url')
        db.session.commit()
        flash(f'Pet {pet.name} updated successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('edit_pet.html', pet=pet)
