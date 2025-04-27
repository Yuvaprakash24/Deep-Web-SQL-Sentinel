# SQL Injection Detection System

A Flask-based web application that detects and prevents SQL injection attacks during user authentication. The system monitors login attempts, identifies malicious queries, and sends email alerts when suspicious activities are detected.

## Features

- User registration and authentication
- SQL injection attack detection
- Real-time email alerts for malicious attempts
- Activity logging and monitoring
- Secure password hashing
- Session management

## Prerequisites

- Python 3.x
- Flask
- Flask-SQLAlchemy
- Flask-Mail
- SQLite3

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python init_db.py
```

## Configuration

1. Update the email settings in `app.py`:
```python
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'
```

2. Set a secure secret key:
```python
app.config['SECRET_KEY'] = 'your-secure-secret-key'
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Access the application at `http://localhost:5000`

3. Register a new user account

4. Test the SQL injection detection:
   - Try logging in with malicious queries like:
     - `' or '1'='1`
     - `admin' --`
     - `1=1`
     - `select * from users`

## Project Structure

```
├── app.py                 # Main application file
├── init_db.py            # Database initialization script
├── requirements.txt      # Project dependencies
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   └── activity.html
└── database/            # Database directory
    └── users.db        # SQLite database file
```

## Security Features

- Password hashing using Werkzeug
- SQL injection pattern detection
- Session management
- Email alerts for suspicious activities
- Secure database operations

## Testing Malicious Attempts

To test the SQL injection detection:
1. Register a user with your email
2. Try logging in with these patterns:
   - `' or '1'='1`
   - `admin' --`
   - `1=1`
   - `select * from users`
3. Check your email for alert messages
4. View the activity log in the dashboard

## Contributing

Feel free to submit issues and enhancement requests.