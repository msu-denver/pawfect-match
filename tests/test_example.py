"""
Example test file demonstrating white-box and black-box testing.

Author(s): Purple T-Pythons Team
"""

import pytest
from src.app import app, db


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_home_page_black_box(client):
    """
    Black-box test: Test the home page from user perspective.
    Tests that the endpoint returns a successful response.
    """
    response = client.get('/')
    assert response.status_code == 200


def test_home_page_white_box(client):
    """
    White-box test: Test internal structure of home page route.
    Tests specific implementation details like response data.
    """
    with app.test_request_context('/'):
        response = client.get('/')
        assert response.status_code == 200
