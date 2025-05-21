import os
import pytest

# Set test database configuration before importing app
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from app import app as flask_app, db

@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    # Configure the app for testing
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.config['WTF_CSRF_ENABLED'] = False
    
    # Create application context
    ctx = flask_app.app_context()
    ctx.push()
    
    # Create all tables
    db.create_all()
    
    yield flask_app
    
    # Clean up
    db.session.remove()
    db.drop_all()
    ctx.pop()

@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    """Create a test CLI runner for the app."""
    return app.test_cli_runner() 