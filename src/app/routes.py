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


@main.route('/dashboard')
# @login_required  # Temporarily disabled for testing
def dashboard():
    """Dashboard showing different views for admin vs adopter."""
    # TODO: Uncomment @login_required after authentication is implemented
    # TEMPORARY: Default to admin view for testing
    pets = Pet.query.all()
    return render_template('admin_dashboard.html', pets=pets)


@main.route('/pet/add', methods=['GET', 'POST'])
# @login_required  # Temporarily disabled for testing
def add_pet():
    """Add a new pet (admin only)."""
    # TODO: Uncomment @login_required after authentication is implemented
    if current_user.is_authenticated and not current_user.is_admin:
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
# @login_required  # Temporarily disabled for testing
def edit_pet(pet_id):
    """Edit pet details (admin only)."""
    # TODO: Uncomment @login_required after authentication is implemented
    if current_user.is_authenticated and not current_user.is_admin:
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

