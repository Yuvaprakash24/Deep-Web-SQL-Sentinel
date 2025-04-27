from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message  # type: ignore
import os
from werkzeug.security import generate_password_hash, check_password_hash

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
        
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('index.html')

def send_email(to_email, attempt_info):
    msg = Message('Alert: Malicious Login Attempt',
                  sender='websqlsentinel@gmail.com',
                  recipients=[to_email])
    msg.body = f'A malicious login attempt was detected with the following details:\n{attempt_info}'
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
                new_attempt = LoginAttempt(user_id=user.id, status='Success', is_malicious=is_malicious)
                db.session.add(new_attempt)
                db.session.commit()

                if is_malicious:
                    attempt_info = f"User ID: {user.id}, Email: {user.email}, Time: {new_attempt.timestamp}"
                    send_email(user.email, attempt_info)

                return redirect(url_for('activity'))
            else:
                new_attempt = LoginAttempt(user_id=user.id, status='Failed', is_malicious=is_malicious)
                db.session.add(new_attempt)
                db.session.commit()

                if is_malicious:
                    attempt_info = f"User ID: {user.id if user else 'Unknown'}, Email: {email}, Time: {new_attempt.timestamp}"
                    send_email(user.email, attempt_info if user else email)

        flash('Login failed. Check your email or password.', 'danger')
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
    with app.app_context():
        db.drop_all()
        db.create_all()
