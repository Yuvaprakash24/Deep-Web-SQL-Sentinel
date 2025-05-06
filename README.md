# SQL Injection Detection System

A Flask-based web application that detects and prevents SQL injection attacks during user authentication. The system monitors login attempts, identifies malicious queries, and sends email alerts when suspicious activities are detected.

## Features

- User registration and authentication
- SQL injection attack detection using Machine Learning
- Real-time email alerts for malicious attempts
- IP-based blocking for malicious users
- Activity logging and monitoring
- Secure password hashing
- Session management
- PostgreSQL database integration
- Vercel deployment ready

## Prerequisites

- Python 3.x
- PostgreSQL database
- Flask
- Flask-SQLAlchemy
- Flask-Mail
- Flask-Migrate
- psycopg2-binary
- scikit-learn (for ML model)

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

4. Create a `.env` file with the following variables:
```env
DATABASE_URL=your_postgresql_connection_string
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SECRET_KEY=your_secure_secret_key
```

5. Initialize the database:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Configuration

The application uses environment variables for configuration. Create a `.env` file with:

```env
DATABASE_URL=postgresql://user:password@host:port/database
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
SECRET_KEY=your-secure-secret-key
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
├── requirements.txt      # Project dependencies
├── vercel.json          # Vercel deployment configuration
├── .env                 # Environment variables (not in version control)
├── MODELS/              # Machine Learning models
│   ├── random_forest_model.py
│   └── train_model.py
└── templates/           # HTML templates
    ├── base.html
    ├── index.html
    ├── login.html
    └── activity.html
```

## Security Features

- Password hashing using Werkzeug
- SQL injection pattern detection using Machine Learning
- IP-based blocking for malicious users
- Session management
- Email alerts for suspicious activities
- Secure database operations with PostgreSQL
- Environment variable protection

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
5. Notice IP blocking for malicious attempts

## Contributing

Feel free to submit issues and enhancement requests.