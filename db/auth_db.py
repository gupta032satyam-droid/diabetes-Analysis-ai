import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def initialize_db():
    """Initializes the SQLite database and creates the users table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vitals_tracker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            glucose REAL,
            bmi REAL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diagnosis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            diagnosis_label TEXT,
            confidence REAL,
            bmi REAL,
            glucose REAL,
            hba1c REAL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password, salt=None):
    """Hashes the password using SHA-256 and a salt."""
    if salt is None:
        salt = os.urandom(16).hex()
    
    # Hash the password with the salt
    hash_obj = hashlib.sha256((password + salt).encode())
    return hash_obj.hexdigest(), salt

def register_user(username, password):
    """Registers a new user in the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Username already exists."

        password_hash, salt = hash_password(password)
        
        cursor.execute('''
            INSERT INTO users (username, password_hash, salt)
            VALUES (?, ?, ?)
        ''', (username, password_hash, salt))
        
        conn.commit()
        conn.close()
        return True, "Registration successful."
    except Exception as e:
        return False, f"Error: {str(e)}"

def authenticate_user(username, password):
    """Authenticates a user by checking the username and password."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT password_hash, salt FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            stored_hash, salt = row
            check_hash, _ = hash_password(password, salt)
            if check_hash == stored_hash:
                return True, username
        
        return False, "Invalid username or password."
    except Exception as e:
        return False, f"Error: {str(e)}"

def save_vitals(username, glucose, bmi):
    """Saves a new glucose and BMI entry for a user."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vitals_tracker (username, glucose, bmi)
            VALUES (?, ?, ?)
        ''', (username, glucose, bmi))
        conn.commit()
        conn.close()
        return True, "Vitals saved successfully."
    except Exception as e:
        return False, str(e)

def get_vitals_history(username):
    """Retrieves the history of vitals for a user."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT glucose, bmi, recorded_at 
            FROM vitals_tracker 
            WHERE username = ? 
            ORDER BY recorded_at DESC
        ''', (username,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"DB Error: {e}")
        return []

def save_diagnosis_history(username, label, confidence, bmi, glucose, hba1c):
    """Saves a diagnostic prediction record for a user."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO diagnosis_history (username, diagnosis_label, confidence, bmi, glucose, hba1c)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, label, confidence, bmi, glucose, hba1c))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"History DB Error: {e}")
        return False

def get_diagnosis_history(username):
    """Retrieves the diagnostic history for a user."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT diagnosis_label, confidence, bmi, glucose, hba1c, recorded_at 
            FROM diagnosis_history 
            WHERE username = ? 
            ORDER BY recorded_at DESC
        ''', (username,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"DB Error: {e}")
        return []
