import sqlite3
import os

# Define the database path
DATABASE_PATH = os.path.join("database", "users.db")

# Ensure the 'database' folder exists
if not os.path.exists("database"):
    os.makedirs("database")

def init_db():
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            # Drop existing tables
            cursor.execute('DROP TABLE IF EXISTS login_attempts')
            cursor.execute('DROP TABLE IF EXISTS users')
            # Create 'users' table if it doesn't exist
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                email TEXT UNIQUE NOT NULL,
                                username TEXT NOT NULL,
                                password TEXT NOT NULL
                              )''')
            # Create 'login_attempts' table if it doesn't exist
            cursor.execute('''CREATE TABLE IF NOT EXISTS login_attempts (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER NOT NULL,
                                status TEXT NOT NULL,
                                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                                is_malicious BOOLEAN DEFAULT 0,
                                FOREIGN KEY(user_id) REFERENCES users(id)
                              )''')
            conn.commit()
            print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_db()
