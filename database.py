import sqlite3

DATABASE = "database.db"


# ---------------------------------------
# Database Connection
# ---------------------------------------
def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------
# Create Tables
# ---------------------------------------
def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT UNIQUE NOT NULL,

        email TEXT UNIQUE NOT NULL,

        password TEXT NOT NULL,

        failed_attempts INTEGER DEFAULT 0,

        locked INTEGER DEFAULT 0,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    # Login History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS login_history (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT NOT NULL,

        login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        ip_address TEXT

    )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------
# Create User
# ---------------------------------------
def create_user(username, email, password):

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO users(username, email, password)
        VALUES(?,?,?)
        """,
        (username, email, password)
    )

    conn.commit()
    conn.close()


# ---------------------------------------
# Get User
# ---------------------------------------
def get_user(username):

    conn = get_connection()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE username=?
        """,
        (username,)
    ).fetchone()

    conn.close()

    return user


# ---------------------------------------
# Failed Login Attempt
# ---------------------------------------
def increase_failed_attempt(username):

    conn = get_connection()

    conn.execute(
        """
        UPDATE users
        SET failed_attempts = failed_attempts + 1
        WHERE username=?
        """,
        (username,)
    )

    conn.commit()
    conn.close()


# ---------------------------------------
# Reset Failed Attempt
# ---------------------------------------
def reset_failed_attempt(username):

    conn = get_connection()

    conn.execute(
        """
        UPDATE users
        SET failed_attempts = 0
        WHERE username=?
        """,
        (username,)
    )

    conn.commit()
    conn.close()


# ---------------------------------------
# Lock Account
# ---------------------------------------
def lock_account(username):

    conn = get_connection()

    conn.execute(
        """
        UPDATE users
        SET locked = 1
        WHERE username=?
        """,
        (username,)
    )

    conn.commit()
    conn.close()


# ---------------------------------------
# Save Login History
# ---------------------------------------
def save_login_history(username, ip):

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO login_history(username, ip_address)
        VALUES(?,?)
        """,
        (username, ip)
    )

    conn.commit()
    conn.close()


# ---------------------------------------
# Get Login History
# ---------------------------------------
def get_login_history():

    conn = get_connection()

    history = conn.execute(
        """
        SELECT *
        FROM login_history
        ORDER BY login_time DESC
        """
    ).fetchall()

    conn.close()

    return history


# ---------------------------------------
# Unlock Account
# ---------------------------------------
def unlock_account(username):

    conn = get_connection()

    conn.execute(
        """
        UPDATE users
        SET locked = 0,
            failed_attempts = 0
        WHERE username=?
        """,
        (username,)
    )

    conn.commit()
    conn.close()


# ---------------------------------------
# Get All Users (Admin)
# ---------------------------------------
def get_all_users():

    conn = get_connection()

    users = conn.execute(
        """
        SELECT
            id,
            username,
            email,
            created_at,
            locked
        FROM users
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return users


# ---------------------------------------
# Initialize Database
# ---------------------------------------
create_tables()