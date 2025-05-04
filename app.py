from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message  # type: ignore
import os
from werkzeug.security import generate_password_hash, check_password_hash
import pytz
from datetime import datetime

app = Flask(__name__)  # Corrected the typo here
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database/users.db')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '21ag1a1220@gmail.com'
app.config['MAIL_PASSWORD'] = 'yxyi fjij mrfu cteg'
mail = Mail(app)

db = SQLAlchemy(app)

# Ensure the database directory exists
os.makedirs(os.path.join(basedir, 'database'), exist_ok=True)

malicious_queries = [
    "1=1", "or '1'='1'", "' or '1'='1'", '" or "1"="1"', "' or '1'='1' -- ", '1" or "1"="1', 
    "select", "drop", "delete", "insert", "update", "alter", "create", "exec", 
    " union ", "xp_cmdshell", "--", ";--", ";", "/", "/", "@@", 
    "char(", "nchar(", "varchar(", "nvarchar(", 
    "'; exec master..xp_cmdshell", "-- ", "' or 1=1 -- ", 
    '" or 1=1 -- ', "' or '' = '", "admin' --", "admin' #", "admin'/*", 
    "admin' or '1'='1", "admin' or '1'='1'--", "admin' or '1'='1'/*", 
    "admin' or 1=1", "admin' or 1=1 --", "admin' or 1=1/*", "admin') or ('1'='1", 
    "admin') or ('1'='1'--", "admin') or ('1'='1'/*", "' or '1'='1", 
    "or 1=1", "or 1=1 --", "or 1=1/", "' or ''='", "' or 1 --", "' or 1/",
    "1' or '1'='1", "1') or ('1'='1", '" or "1"="1', '" or "1"="1" --', '" or "1"="1"/*',
    "select * from 1==1"  
]

class User(db.Model):
    __tablename__ = 'users'  # Match the table name in init_db.py
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)

class LoginAttempt(db.Model):
    __tablename__ = 'login_attempts'  # Match the table name in init_db.py
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Update foreign key reference
    status = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_malicious = db.Column(db.Boolean, default=False)

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
                <p>© 2024 Deep Web SQL Sentinel. All rights reserved.</p>
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
        is_malicious = any(keyword in password.lower() for keyword in malicious_queries)
        
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                session['user_id'] = user.id
                # Use IST for timestamp
                ist = pytz.timezone('Asia/Kolkata')
                now_ist = datetime.now(ist)
                new_attempt = LoginAttempt(user_id=user.id, status='Success', is_malicious=is_malicious, timestamp=now_ist)
                db.session.add(new_attempt)
                db.session.commit()

                if is_malicious:
                    attempt_info = f"User ID: {user.id}, Email: {user.email}, Time: {new_attempt.timestamp.strftime('%d-%m-%Y %I:%M:%S %p')}"
                    send_email(user.email, attempt_info)

                return redirect(url_for('activity'))
            else:
                ist = pytz.timezone('Asia/Kolkata')
                now_ist = datetime.now(ist)
                new_attempt = LoginAttempt(user_id=user.id, status='Failed', is_malicious=is_malicious, timestamp=now_ist)
                db.session.add(new_attempt)
                db.session.commit()

                if is_malicious:
                    attempt_info = f"User ID: {user.id if user else 'Unknown'}, Email: {email}, Time: {new_attempt.timestamp.strftime('%d-%m-%Y %I:%M:%S %p')}"
                    send_email(user.email, attempt_info if user else email)
                else:
                    flash('Invalid email or password.', 'danger')
        else:
            # No user found, but still check for malicious
            if is_malicious:
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
    return render_template('activity.html', user=user, attempts=attempts)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':  # Corrected the typo here
    app.run(debug=True)
    
    # Drop and recreate the database
    # with app.app_context():
    #     db.drop_all()
    #     db.create_all()
