from flask import Flask, render_template, redirect, url_for, request, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message  # type: ignore
from flask_migrate import Migrate
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
from MODELS.random_forest_model import check_login_attempt  # Import the model function
from dotenv import load_dotenv
# from MODELS.logistic_regression_model import check_login_attempt
# Retrain the model every time the server starts
exec(open('MODELS/train_model.py').read())
from werkzeug.middleware.proxy_fix import ProxyFix
import pytz

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Add ProxyFix middleware
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')
mail = Mail(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Ensure the database directory exists
os.makedirs(os.path.join(basedir, 'database'), exist_ok=True)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(500), nullable=False)

class LoginAttempt(db.Model):
    __tablename__ = 'login_attempts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_malicious = db.Column(db.Boolean, default=False)
    is_suspicious = db.Column(db.Boolean, default=False)
    ip_address = db.Column(db.String(50), nullable=True)  # Made nullable initially

class BlockedIP(db.Model):
    __tablename__ = 'blocked_ips'
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), unique=True, nullable=False)
    blocked_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    reason = db.Column(db.String(200), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)  # None means permanent block

@app.before_request
def check_blocked_ip():
    if request.endpoint and 'static' not in request.endpoint:
        ip = request.remote_addr
        blocked = BlockedIP.query.filter_by(ip_address=ip).first()
        if blocked:
            if blocked.expires_at is None or blocked.expires_at > datetime.now():
                abort(403)  # Forbidden
            else:
                # Remove expired block
                db.session.delete(blocked)
                db.session.commit()

def block_ip(ip_address, reason, duration_days=None):
    expires_at = None
    if duration_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=duration_days)
    
    blocked = BlockedIP(
        ip_address=ip_address,
        reason=reason,
        expires_at=expires_at
    )
    db.session.add(blocked)
    db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return render_template('index.html')
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('index.html')

def send_email(to_email, attempt_info):
    msg = Message('🔒 Security Alert: Suspicious Activity Detected',
                  sender='websqlsentinel@gmail.com',
                  recipients=[to_email])
    
    # HTML email template
    html_template = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #1e3a8a;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 0 0 5px 5px;
                }}
                .alert {{
                    color: #d32f2f;
                    font-weight: bold;
                }}
                .details {{
                    background-color: #fff;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 15px 0;
                }}
                .footer {{
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>Deep Web SQL Sentinel</h2>
            </div>
            <div class="content">
                <h3>Security Alert</h3>
                <p class="alert">⚠️ Suspicious activity has been detected on your account</p>
                
                <div class="details">
                    <p><strong>Activity Details:</strong></p>
                    <p>{attempt_info}</p>
                </div>
                
                <p>If you did not perform this action, please:</p>
                <ul>
                    <li>Change your password immediately</li>
                    <li>Review your recent activity</li>
                    <li>Contact support if you suspect unauthorized access</li>
                </ul>
                
                <p>For your security, we recommend enabling two-factor authentication if you haven't already.</p>
            </div>
            <div class="footer">
                <p>This is an automated security alert. Please do not reply to this email.</p>
                <p>© 2025 Deep Web SQL Sentinel. All rights reserved.</p>
            </div>
        </body>
    </html>
    """
    
    msg.html = html_template
    mail.send(msg)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Debug logging for login attempt
        print("\n=== Login Attempt Debug Info ===")
        ip_address = get_client_ip()
        print(f"Final IP used for login attempt: {ip_address}")
        
        user = User.query.filter_by(email=email).first()
        if user:
            # Use the Random Forest model to check the login attempt
            result = check_login_attempt(user, request)
            is_malicious = result == 'malicious'
            is_suspicious = result == 'suspicious'
            
            if check_password_hash(user.password, password):
                session['user_id'] = user.id
                now_utc = datetime.now(timezone.utc)
                new_attempt = LoginAttempt(
                    user_id=user.id, 
                    status='Success', 
                    is_malicious=is_malicious,
                    is_suspicious=is_suspicious,
                    ip_address=ip_address,
                    timestamp=now_utc
                )
                db.session.add(new_attempt)
                db.session.commit()
                print(f"Login attempt logged with IP: {ip_address}")

                # Block IP if malicious
                if is_malicious:
                    block_ip(ip_address, "Malicious login attempt detected", duration_days=30)
                    attempt_info = f"User ID: {user.id}, Email: {user.email}, Time: {new_attempt.timestamp.strftime('%d-%m-%Y %I:%M:%S %p')}, IP: {ip_address}"
                    send_email(user.email, attempt_info)
                    print(f"Malicious attempt blocked for IP: {ip_address}")

                return redirect(url_for('activity'))
            else:
                now_utc = datetime.now(timezone.utc)
                new_attempt = LoginAttempt(
                    user_id=user.id, 
                    status='Failed', 
                    is_malicious=is_malicious,
                    is_suspicious=is_suspicious,
                    ip_address=ip_address,
                    timestamp=now_utc
                )
                db.session.add(new_attempt)
                db.session.commit()
                print(f"Failed login attempt logged with IP: {ip_address}")

                # Block IP if malicious
                if is_malicious:
                    block_ip(ip_address, "Malicious login attempt detected", duration_days=30)
                    attempt_info = f"User ID: {user.id if user else 'Unknown'}, Email: {email}, Time: {new_attempt.timestamp.strftime('%d-%m-%Y %I:%M:%S %p')}, IP: {ip_address}"
                    send_email(user.email, attempt_info)
                    print(f"Malicious attempt blocked for IP: {ip_address}")
                else:
                    flash('Invalid email or password.', 'danger')
        else:
            # Check for non-existent user
            result = check_login_attempt(None, request)
            is_malicious = result == 'malicious'
            is_suspicious = result == 'suspicious'
            
            if is_malicious:
                block_ip(ip_address, "Malicious login attempt detected", duration_days=30)
                flash('Login failed. Check your email or password.', 'danger')
            else:
                flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/activity')
def activity():
    if 'user_id' not in session:
        flash('Please log in first.', 'danger')
        return redirect(url_for('login'))
    user_id = session['user_id']
    user = User.query.get(user_id)
    attempts = LoginAttempt.query.filter_by(user_id=user_id).all()
    ist = pytz.timezone('Asia/Kolkata')
    # Ensure all timestamps are UTC-aware
    for attempt in attempts:
        if attempt.timestamp and attempt.timestamp.tzinfo is None:
            attempt.timestamp = attempt.timestamp.replace(tzinfo=timezone.utc)
    return render_template('activity.html', user=user, attempts=attempts, ist=ist)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

def get_client_ip():
    """
    Get the real client IP address by checking various headers.
    Returns the first non-private IP address found.
    """
    # Debug logging
    print("\n=== IP Detection Debug Info ===")
    print(f"Remote Addr: {request.remote_addr}")
    print("All Headers:")
    for header, value in request.headers.items():
        print(f"{header}: {value}")
    
    # List of headers to check for IP address
    headers = [
        'X-Forwarded-For',
        'X-Real-IP',
        'CF-Connecting-IP',  # Cloudflare
        'True-Client-IP',    # Akamai
        'X-Client-IP'        # Custom
    ]
    
    # Check each header
    for header in headers:
        ip = request.headers.get(header)
        if ip:
            # X-Forwarded-For can contain multiple IPs
            if header == 'X-Forwarded-For':
                ip = ip.split(',')[0].strip()
            print(f"Found IP from {header}: {ip}")
            return ip
    
    print("No IP found in headers, using remote_addr")
    return request.remote_addr

if __name__ == '__main__':
    app.run(debug=True)
