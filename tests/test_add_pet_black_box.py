"""
Black box tests for adding a pet functionality.

Author(s): Purple T-Pythons Team
"""

import pytest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from app import create_app, db
from app.models import User, Pet


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
   
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def admin_user(app):
    """Create an admin user for testing."""
    with app.app_context():
        admin = User(username='admin', email='admin@test.com', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        return admin


def login_admin(client):
    """Helper function to log in as admin."""
    return client.post('/login', data={
        'email': 'admin@test.com',
        'password': 'admin123'
    }, follow_redirects=True)


class TestAddPetBlackBox:
    """Black box tests for adding pets - testing inputs and outputs only."""
   
    def test_add_pet_with_valid_data(self, client, admin_user):
        """Test adding a pet with all valid data."""
        # Login as admin
        login_admin(client)
       
        # Submit form with valid pet data
        response = client.post('/pet/add', data={
            'name': 'Max',
            'species': 'Dog',
            'breed': 'Golden Retriever',
            'age_value': '2',
            'age_unit': 'years',
            'gender': 'Male',
            'spayed_neutered': 'on',
            'vaccinated': 'on',
            'description': 'Friendly and energetic dog',
            'image_url': 'https://example.com/max.jpg'
        }, follow_redirects=True)
       
        # Verify pet was added successfully
        assert response.status_code == 200
        assert b'Pet Max added successfully!' in response.data
       
        # Verify pet appears in dashboard
        response = client.get('/dashboard')
        assert b'Max' in response.data
        assert b'Golden Retriever' in response.data
   
    def test_add_pet_with_age_in_months(self, client, admin_user):
        """Test adding a pet with age in months."""
        login_admin(client)
       
        response = client.post('/pet/add', data={
            'name': 'Whiskers',
            'species': 'Cat',
            'breed': 'Siamese',
            'age_value': '6',
            'age_unit': 'months',
            'gender': 'Female',
            'description': 'Playful kitten'
        }, follow_redirects=True)
       
        assert response.status_code == 200
        assert b'Pet Whiskers added successfully!' in response.data
       
        # Verify age is formatted correctly
        response = client.get('/dashboard')
        assert b'6 months' in response.data
   
    def test_add_pet_with_singular_age(self, client, admin_user):
        """Test that age formatting handles singular correctly (1 year, not 1 years)."""
        login_admin(client)
       
        response = client.post('/pet/add', data={
            'name': 'Buddy',
            'species': 'Dog',
            'breed': 'Beagle',
            'age_value': '1',
            'age_unit': 'years',
            'gender': 'Male'
        }, follow_redirects=True)
       
        assert response.status_code == 200
       
        # Check that it's "1 year" not "1 years"
        response = client.get('/dashboard')
        assert b'1 year' in response.data
        assert b'1 years' not in response.data
   
    def test_add_pet_without_optional_fields(self, client, admin_user):
        """Test adding a pet with only required fields."""
        login_admin(client)
       
        response = client.post('/pet/add', data={
            'name': 'Lucky',
            'species': 'Dog'
        }, follow_redirects=True)
       
        assert response.status_code == 200
        assert b'Pet Lucky added successfully!' in response.data
   
    def test_add_pet_with_cat_species(self, client, admin_user):
        """Test adding a cat."""
        login_admin(client)
       
        response = client.post('/pet/add', data={
            'name': 'Mittens',
            'species': 'Cat',
            'breed': 'Persian',
            'age_value': '3',
            'age_unit': 'years',
            'gender': 'Female'
        }, follow_redirects=True)
       
        assert response.status_code == 200
        assert b'Pet Mittens added successfully!' in response.data
       
        # Verify cat appears in dashboard
        response = client.get('/dashboard')
        assert b'Mittens' in response.data
        assert b'Cat' in response.data
   
    def test_add_multiple_pets(self, client, admin_user):
        """Test adding multiple pets."""
        login_admin(client)
       
        # Add first pet
        client.post('/pet/add', data={
            'name': 'Rex',
            'species': 'Dog',
            'breed': 'Labrador'
        }, follow_redirects=True)
       
        # Add second pet
        client.post('/pet/add', data={
            'name': 'Fluffy',
            'species': 'Cat',
            'breed': 'Maine Coon'
        }, follow_redirects=True)
       
        # Verify both pets appear in dashboard
        response = client.get('/dashboard')
        assert b'Rex' in response.data
        assert b'Fluffy' in response.data
   
    def test_non_admin_cannot_add_pet(self, client, app):
        """Test that non-admin users cannot add pets."""
        # Create and login as regular user
        with app.app_context():
            user = User(username='user', email='user@test.com', is_admin=False)
            user.set_password('user123')
            db.session.add(user)
            db.session.commit()
       
        client.post('/login', data={
            'email': 'user@test.com',
            'password': 'user123'
        }, follow_redirects=True)
       
        # Try to add pet as non-admin
        response = client.post('/pet/add', data={
            'name': 'TestPet',
            'species': 'Dog'
        }, follow_redirects=True)
       
        # Should be redirected or see error message
        assert b'Only admins can add pets' in response.data
   
    def test_add_pet_without_login(self, client, admin_user):
        """Test that unauthenticated users cannot add pets."""
        response = client.post('/pet/add', data={
            'name': 'TestPet',
            'species': 'Dog'
        }, follow_redirects=True)
       
        # Should be redirected to login/register
        assert response.status_code == 200
        assert b'register' in response.data.lower() or b'login' in response.data.lower()
   
    def test_add_pet_with_special_characters_in_name(self, client, admin_user):
        """Test adding a pet with special characters in the name."""
        login_admin(client)
       
        response = client.post('/pet/add', data={
            'name': "Mr. Whiskers O'Malley",
            'species': 'Cat',
            'breed': 'Tabby'
        }, follow_redirects=True)
       
        assert response.status_code == 200
        assert b'Pet Mr. Whiskers O&#39;Malley added successfully!' in response.data or \
               b"Pet Mr. Whiskers O'Malley added successfully!" in response.data
   
    def test_add_pet_with_long_description(self, client, admin_user):
        """Test adding a pet with a long description."""
        login_admin(client)
       
        long_description = "This is a very friendly and energetic dog who loves to play fetch. " * 10
       
        response = client.post('/pet/add', data={
            'name': 'Charlie',
            'species': 'Dog',
            'description': long_description
        }, follow_redirects=True)
       
        assert response.status_code == 200
        assert b'Pet Charlie added successfully!' in response.data
