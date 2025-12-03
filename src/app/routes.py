"""
Application routes and views.

Author(s): Purple T-Pythons Team
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .models import User, Pet

main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Home page with mission and links to dogs/cats."""
    return render_template('index.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            # Clear any existing flash messages before adding success message
            flash("Logged in successfully!", "success")
            
            # Redirect to the page they were trying to access, or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
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
        
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash("Username already taken. Please choose another.", "danger")
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
        
        # Clear any existing flash messages before adding success message
        session.pop('_flashes', None)
        flash("Account created successfully!", "success")
        
        # Redirect to the page they were trying to access, or dashboard
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
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
        # Handle age formatting
        age_value = request.form.get('age_value')
        age_unit = request.form.get('age_unit')
        age_formatted = None
        if age_value and age_unit:
            age_num = int(age_value)
            if age_num == 1:
                age_formatted = f"1 {age_unit[:-1]}"  # Remove 's' for singular
            else:
                age_formatted = f"{age_num} {age_unit}"
        
        pet = Pet(
            name=request.form.get('name'),
            species=request.form.get('species'),
            breed=request.form.get('breed'),
            age=age_formatted,
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
        # Handle age formatting
        age_value = request.form.get('age_value')
        age_unit = request.form.get('age_unit')
        age_formatted = None
        if age_value and age_unit:
            age_num = int(age_value)
            if age_num == 1:
                age_formatted = f"1 {age_unit[:-1]}"  # Remove 's' for singular
            else:
                age_formatted = f"{age_num} {age_unit}"
        
        pet.name = request.form.get('name')
        pet.species = request.form.get('species')
        pet.breed = request.form.get('breed')
        pet.age = age_formatted
        pet.description = request.form.get('description')
        pet.status = request.form.get('status')
        pet.image_url = request.form.get('image_url')
        db.session.commit()
        flash(f'Pet {pet.name} updated successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    # Parse existing age for editing
    age_value = ''
    age_unit = ''
    if pet.age:
        # Handle old integer format (for backward compatibility)
        if isinstance(pet.age, int):
            age_value = str(pet.age)
            age_unit = 'years'
        # Handle new string format
        elif isinstance(pet.age, str):
            parts = pet.age.split()
            if len(parts) >= 2:
                age_value = parts[0]
                # Handle both singular and plural
                if parts[1] in ['month', 'months']:
                    age_unit = 'months'
                elif parts[1] in ['year', 'years']:
                    age_unit = 'years'
    
    return render_template('edit_pet.html', pet=pet, age_value=age_value, age_unit=age_unit)


@main.route('/dogs')
@login_required
def view_dogs():
    """View all available dogs (requires login)."""
    dogs = Pet.query.filter_by(species='Dog', status='available').all()
    return render_template('view_pets.html', pets=dogs, species='Dogs')


@main.route('/cats')
@login_required
def view_cats():
    """View all available cats (requires login)."""
    cats = Pet.query.filter_by(species='Cat', status='available').all()
    return render_template('view_pets.html', pets=cats, species='Cats')
