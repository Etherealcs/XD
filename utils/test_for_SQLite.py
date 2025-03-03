import sqlite3
import hashlib

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        print("User registered successfully!")
    except sqlite3.IntegrityError:
        print("Username already exists.")
    finally:
        conn.close()

def check_login(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result and result[0] == hash_password(password):
        return True
    return False

# Example usage:
register_user('john', 'johnspassword')
if check_login('john', 'johnspassword'):
    print("Login successful!")
else:
    print("Login failed!")
