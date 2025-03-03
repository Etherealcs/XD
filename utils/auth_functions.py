import streamlit as st
import utils.database as db
import re
import streamlit as st
import sqlite3
import hashlib


def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# Insert a new user into the database
def create_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    # Check if username already exists
    cur.execute('SELECT * FROM users WHERE username = ?', (username,))
    if cur.fetchone():
        return False
    # Insert new user
    cur.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                (username, hash_password(password)))
    conn.commit()
    conn.close()
    return True

# Check user credentials
def check_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cur.fetchone()
    conn.close()
    if user and user['password'] == hash_password(password):
        return True
    return False









def is_email_valid(email):
    # Simple regex for validating an email
    pattern = r"^\S+@\S+\.\S+$"
    return re.match(pattern, email)

def is_password_strong(password):
    # Check if the password is at least 6 characters
    if len(password) < 6:
        return False
    return True

def is_email_unique(email):
    # Check if the email is already in the database
    return not db.is_user_exist(email)

def passwords_match(password, repeated_password):
    # Check if both passwords match
    return password == repeated_password

def register_user():
    with st.form("Register User Form"):
        st.subheader("用户注册")
        username = st.text_input("用户名*")
        password = st.text_input("账户密码*", type="password")
        repeated_password = st.text_input("重复密码*", type="password")
        submit_button = st.form_submit_button("Register")

        if submit_button:
            if create_user(username, password):
                st.success('You have successfully created a valid account')
                st.info('Go to Login Menu to login')
            else:
                st.warning('Username already exists')
            return True
    return False


def login():
    with st.form("login_form"):
        st.subheader("登录")
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        submit_button = st.form_submit_button("登录")

        if submit_button:
            if check_user(username, password):
                st.success('Logged In as {}'.format(username))
                st.session_state["authentication_status"] = True
                st.session_state["name"] = username

                st.rerun()
            else:
                st.warning('Incorrect Username/Password')

def logout():
    st.session_state["authentication_status"] = None
    st.session_state["authentication_status_teacher"] = None
    st.session_state["authentication_status_student"] = None
    st.session_state["name"] = None
    st.session_state["email"] = None
    st.rerun()