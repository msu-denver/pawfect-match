"""
White box tests for the Pet Adoption application. 

Author(s): Purple T-Pythons Team
"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from app import create_app, db
from app.models import User, Pet

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def admin_user(app):
    """Creates an admin user to attach to session manually."""
    with app.app_context():
        user = User(username="admin", email="admin@example.com", is_admin=True)
        user.set_password("test123")
        db.session.add(user)
        db.session.commit()
        return user
        
        
# Test 1 — Pet model saves correctly

def test_pet_model_save(app):
    with app.app_context():
        pet = Pet(name="Milo", species="Dog", age="2 years", status="available")
        db.session.add(pet)
        db.session.commit()

        saved = Pet.query.first()
        assert saved.name == "Milo"
        assert saved.status == "available"


# Helper: simulate login WITHOUT using /login route

def force_login(client, user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)  # how Flask-Login stores session user id
        sess["_fresh"] = True


# Test 2 — Add pet route works

def test_add_pet_route(app, client, admin_user):
    force_login(client, admin_user)

    response = client.post("/pet/add", data={
        "name": "Luna",
        "species": "Cat",
        "age_value": "3",
        "age_unit": "years",
        "gender": "Female",
        "description": "Sweet kitty",
        "image_url": "http://example.com/photo.jpg"
    }, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        pet = Pet.query.filter_by(name="Luna").first()
        assert pet is not None
        assert pet.age == "3 years"


# Test 3 — Edit pet updates fields and reformats age

def test_edit_pet_route(app, client, admin_user):
    with app.app_context():
        pet = Pet(name="Leo", species="Dog", age="1 year", status="available")
        db.session.add(pet)
        db.session.commit()
        pet_id = pet.id

    force_login(client, admin_user)

    response = client.post(f"/pet/{pet_id}/edit", data={
        "name": "Leo Updated",
        "species": "Dog",
        "breed": "Husky",
        "age_value": "2",
        "age_unit": "years",
        "description": "Updated desc",
        "status": "pending",
        "image_url": ""
    }, follow_redirects=True)

    assert response.status_code == 200

    with app.app_context():
        updated = Pet.query.get(pet_id)
        assert updated.name == "Leo Updated"
        assert updated.age == "2 years"
        assert updated.status == "pending"


# Test 4 — Delete pet removes entry

def test_delete_pet_route(app, client, admin_user):
    with app.app_context():
        pet = Pet(name="Max", species="Dog", age="4 years", status="available")
        db.session.add(pet)
        db.session.commit()
        pet_id = pet.id

    force_login(client, admin_user)

    response = client.post(f"/pet/{pet_id}/delete", follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        removed = Pet.query.get(pet_id)
        assert removed is None


# Test 5 — Dashboard loads and displays pets

def test_dashboard_lists_pets(app, client, admin_user):
    with app.app_context():
        pet = Pet(name="Buddy", species="Dog", status="available")
        db.session.add(pet)
        db.session.commit()

    force_login(client, admin_user)

    response = client.get("/dashboard")
    assert b"Buddy" in response.data
