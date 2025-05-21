import pytest
from app import db, User, LoginAttempt, BlockedIP
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash

def test_index_page(client):
    """Test that the index page loads successfully"""
    response = client.get('/')
    assert response.status_code == 200

def test_registration(client, app):
    """Test successful user registration"""
    response = client.post('/register', data={
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'testpass123',
        'confirm_password': 'testpass123'
    }, follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        assert user is not None
        assert user.username == 'testuser'

def test_registration_password_mismatch(client, app):
    """Test registration with mismatched passwords"""
    response = client.post('/register', data={
        'email': 'newuser@example.com',
        'username': 'newuser',
        'password': 'newpass123',
        'confirm_password': 'differentpass'
    }, follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        user = User.query.filter_by(email='newuser@example.com').first()
        assert user is None

def test_login_success(client, app):
    """Test successful login"""
    # First create a test user
    with app.app_context():
        user = User(
            email='login@example.com',
            username='loginuser',
            password=generate_password_hash('loginpass123')
        )
        db.session.add(user)
        db.session.commit()

    # Try to login
    response = client.post('/login', data={
        'email': 'login@example.com',
        'password': 'loginpass123'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_login_failure(client):
    """Test login failure with incorrect password"""
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'wrongpass'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_block_ip(client, app):
    """Test IP blocking functionality"""
    with app.app_context():
        # First create and login as a test user
        user = User(
            email='block@example.com',
            username='blockuser',
            password=generate_password_hash('blockpass123')
        )
        db.session.add(user)
        db.session.commit()

        # Login
        client.post('/login', data={
            'email': 'block@example.com',
            'password': 'blockpass123'
        })

        # First ensure no existing block
        BlockedIP.query.filter_by(ip_address='192.168.1.1').delete()
        db.session.commit()

        # Block an IP
        response = client.post('/block_ip/192.168.1.1', follow_redirects=True)
        assert response.status_code == 200

        # Verify IP is blocked
        blocked = BlockedIP.query.filter_by(ip_address='192.168.1.1').first()
        assert blocked is not None

def test_unblock_ip(client, app):
    """Test IP unblocking functionality"""
    with app.app_context():
        # First create and login as a test user
        user = User(
            email='unblock@example.com',
            username='unblockuser',
            password=generate_password_hash('unblockpass123')
        )
        db.session.add(user)
        db.session.commit()

        # Login
        client.post('/login', data={
            'email': 'unblock@example.com',
            'password': 'unblockpass123'
        })

        # First ensure no existing block
        BlockedIP.query.filter_by(ip_address='192.168.1.1').delete()
        db.session.commit()

        # Block an IP
        blocked = BlockedIP(
            ip_address='192.168.1.1',
            reason='Test block',
            blocked_at=datetime.now(timezone.utc)
        )
        db.session.add(blocked)
        db.session.commit()

        # Unblock the IP
        response = client.post('/unblock_ip/192.168.1.1', follow_redirects=True)
        assert response.status_code == 200

        # Verify IP is unblocked
        blocked = BlockedIP.query.filter_by(ip_address='192.168.1.1').first()
        assert blocked is None

def test_login_attempt_recording(client, app):
    """Test that login attempts are recorded"""
    with app.app_context():
        # First create a test user
        user = User(
            email='attempt@example.com',
            username='attemptuser',
            password=generate_password_hash('attemptpass123')
        )
        db.session.add(user)
        db.session.commit()

        # Make a login attempt
        client.post('/login', data={
            'email': 'attempt@example.com',
            'password': 'attemptpass123'
        })

        # Check if attempt was recorded
        attempt = LoginAttempt.query.filter_by(user_id=user.id).first()
        assert attempt is not None
        assert attempt.status == 'Success'

def test_logout(client):
    """Test logout functionality"""
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200

def test_activity_page_requires_login(client):
    """Test that activity page requires login"""
    response = client.get('/activity', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in first' in response.data 