 import os
import secrets

# Flask Secret Key
SECRET_KEY = secrets.token_hex(32)

# SQLite Database
DATABASE = "database.db"

# QR Code Folder
QR_FOLDER = os.path.join("static", "qr")

# Automatically create QR folder
if not os.path.exists(QR_FOLDER):
    os.makedirs(QR_FOLDER)

# Maximum Failed Login Attempts
MAX_FAILED_ATTEMPTS = 5

# Application Name
APP_NAME = "Secure Login System"

# Admin Credentials
# (For demo purposes only. In production, store securely.)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin@123"