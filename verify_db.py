import sqlite3
import os

DATABASE_PATH = os.path.join("database", "users.db")

def verify_db():
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print("Tables in database:", tables)

            # Check 'users' table schema
            cursor.execute("PRAGMA table_info(users);")
            user_schema = cursor.fetchall()
            print("\n'users' table schema:")
            for column in user_schema:
                print(column)

            # Check 'login_attempts' table schema
            cursor.execute("PRAGMA table_info(login_attempts);")
            login_attempts_schema = cursor.fetchall()
            print("\n'login_attempts' table schema:")
            for column in login_attempts_schema:
                print(column)

            # Insert and query test data (optional)
            cursor.execute("INSERT INTO users (email, username, password) VALUES ('test@example.com', 'testuser', 'testpassword');")
            conn.commit()
            cursor.execute("SELECT * FROM users;")
            users = cursor.fetchall()
            print("\nTest data in 'users' table:")
            for user in users:
                print(user)
    except Exception as e:
        print(f"Error verifying database: {e}")

if __name__ == "__main__":
    verify_db()
