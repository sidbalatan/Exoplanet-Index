"""
ExoX - Mod1: Registration & Authentication
User registration with email OTP verification
"""

import streamlit as st
import json
import os
import hashlib
import random
import re
import time
from datetime import datetime, timedelta

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Register - ExoX",
    page_icon=":lock:",
    layout="wide"
)

# ============================================
# CONFIGURATION
# ============================================
USERS_DIR = "users"
USERS_DB = os.path.join(USERS_DIR, "users_database.json")
OTP_EXPIRY_MINUTES = 10
MAX_LOGIN_ATTEMPTS = 5
DEMO_MODE = True  # Set to False when email is configured

# Create users directory if not exists
os.makedirs(USERS_DIR, exist_ok=True)

# ============================================
# DATABASE FUNCTIONS
# ============================================

def load_users_db():
    """Load users database from JSON file."""
    if os.path.exists(USERS_DB):
        with open(USERS_DB, 'r') as f:
            return json.load(f)
    return {"users": {}}

def save_users_db(db):
    """Save users database to JSON file."""
    with open(USERS_DB, 'w') as f:
        json.dump(db, f, indent=2)

def hash_password(password):
    """Hash password with SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_otp():
    """Generate 6-digit OTP."""
    return str(random.randint(100000, 999999))

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
if 'auth_stage' not in st.session_state:
    st.session_state.auth_stage = 'login'
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'otp_code' not in st.session_state:
    st.session_state.otp_code = None
if 'registration_data' not in st.session_state:
    st.session_state.registration_data = {}

# ============================================
# HEADER
# ============================================
st.title("ExoX")
st.subheader("Account Access")

# ============================================
# LOGIN VIEW
# ============================================
if not st.session_state.logged_in and st.session_state.auth_stage == 'login':

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        st.markdown("### Login")

        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            if st.button("Login", type="primary", use_container_width=True):
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    db = load_users_db()
                    if username not in db["users"]:
                        st.error("Invalid username or password.")
                    elif db["users"][username]["password_hash"] != hash_password(password):
                        st.error("Invalid username or password.")
                    elif not db["users"][username].get("email_verified", False):
                        st.error("Email not verified. Please complete registration.")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.success("Login successful!")
                        time.sleep(1)
                        st.switch_page("Home.py")

        with col_btn2:
            if st.button("Create Account", use_container_width=True):
                st.session_state.auth_stage = 'register'
                st.rerun()

# ============================================
# REGISTRATION VIEW
# ============================================
elif not st.session_state.logged_in and st.session_state.auth_stage == 'register':

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        st.markdown("### Create Account")

        new_username = st.text_input("Choose Username", key="reg_username")
        new_email = st.text_input("Email Address", key="reg_email")
        new_password = st.text_input("Choose Password", type="password", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")

        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            if st.button("Back to Login", use_container_width=True):
                st.session_state.auth_stage = 'login'
                st.rerun()

        with col_btn2:
            if st.button("Send Code", type="primary", use_container_width=True):
                errors = []

                if not new_username or len(new_username) < 3:
                    errors.append("Username must be at least 3 characters.")
                if not new_email or "@" not in new_email:
                    errors.append("Please enter a valid email.")
                if not new_password or len(new_password) < 8:
                    errors.append("Password must be at least 8 characters.")
                if new_password != confirm_password:
                    errors.append("Passwords do not match.")

                db = load_users_db()
                if new_username in db["users"]:
                    errors.append("Username already exists.")

                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    otp = generate_otp()
                    st.session_state.otp_code = otp
                    st.session_state.registration_data = {
                        "username": new_username,
                        "email": new_email,
                        "password": new_password,
                        "otp": otp,
                        "otp_expires": (datetime.now() + timedelta(minutes=OTP_EXPIRY_MINUTES)).isoformat()
                    }
                    st.session_state.auth_stage = 'otp'
                    st.rerun()

# ============================================
# OTP VERIFICATION VIEW
# ============================================
elif not st.session_state.logged_in and st.session_state.auth_stage == 'otp':

    reg_data = st.session_state.registration_data

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        st.markdown("### Verify Email")
        st.markdown(f"A verification code was sent to **{reg_data.get('email', 'your email')}**.")

        if DEMO_MODE and st.session_state.otp_code:
            st.info(f"Demo Mode - Your code: **{st.session_state.otp_code}**")

        otp_input = st.text_input("Enter Code", max_chars=6, key="otp_input")

        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            if st.button("Back", use_container_width=True):
                st.session_state.auth_stage = 'register'
                st.rerun()

        with col_btn2:
            if st.button("Verify", type="primary", use_container_width=True):
                expires = datetime.fromisoformat(reg_data.get("otp_expires", ""))
                if datetime.now() > expires:
                    st.error("Code expired. Please register again.")
                    st.session_state.auth_stage = 'register'
                    st.rerun()
                elif otp_input == reg_data.get("otp", ""):
                    db = load_users_db()
                    username = reg_data["username"]
                    db["users"][username] = {
                        "username": username,
                        "email": reg_data["email"],
                        "password_hash": hash_password(reg_data["password"]),
                        "email_verified": True,
                        "registered_at": datetime.now().isoformat(),
                        "last_login": None
                    }
                    save_users_db(db)

                    # Create user folder
                    user_folder = os.path.join(USERS_DIR, username)
                    os.makedirs(os.path.join(user_folder, "docs"), exist_ok=True)
                    os.makedirs(os.path.join(user_folder, "plots"), exist_ok=True)
                    os.makedirs(os.path.join(user_folder, "pipeline_runs"), exist_ok=True)
                    os.makedirs(os.path.join(user_folder, "gallery_uploads"), exist_ok=True)

                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("Account created successfully!")
                    time.sleep(2)
                    st.switch_page("Home.py")
                else:
                    st.error("Invalid code. Please try again.")

# ============================================
# LOGGED IN VIEW
# ============================================
elif st.session_state.logged_in:

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        st.markdown(f"### Welcome, {st.session_state.username}!")
        st.markdown("You are logged in.")

        if st.button("Go to Dashboard", type="primary", use_container_width=True):
            st.switch_page("pages/12_Dashboard.py")

        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.auth_stage = 'login'
            st.rerun()
