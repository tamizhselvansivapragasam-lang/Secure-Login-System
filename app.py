from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    flash
)

from flask_bcrypt import Bcrypt
import sqlite3

from database import (
    create_user,
    get_user,
    increase_failed_attempt,
    reset_failed_attempt,
    lock_account,
    save_login_history,
    get_all_users
)

app = Flask(__name__)

app.secret_key = "SecureLoginProject123"

bcrypt = Bcrypt(app)


# ------------------------------------
# Home
# ------------------------------------

@app.route("/")
def home():

    return render_template("index.html")


# ------------------------------------
# Register
# ------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"].strip()

        email = request.form["email"].strip()

        password = request.form["password"]

        confirm = request.form["confirm"]

        if username == "" or email == "" or password == "":

            flash("Please fill all fields.")

            return redirect("/register")

        if password != confirm:

            flash("Passwords do not match.")

            return redirect("/register")

        if len(password) < 8:

            flash("Password must contain at least 8 characters.")

            return redirect("/register")

        if get_user(username):

            flash("Username already exists.")

            return redirect("/register")

        hashed_password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        try:

            create_user(
                username,
                email,
                hashed_password
            )

            flash("Registration Successful!")

            return redirect("/login")

        except Exception as e:

            print(e)

            flash("Registration Failed!")

            return redirect("/register")

    return render_template("register.html")


# ------------------------------------
# Login
# ------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"].strip()

        password = request.form["password"]

        user = get_user(username)

        if user is None:

            flash("Invalid Username")

            return redirect("/login")

        if user["locked"] == 1:

            flash("Account Locked!")

            return redirect("/login")

        if bcrypt.check_password_hash(
                user["password"],
                password
        ):

            reset_failed_attempt(username)

            session["user"] = username

            save_login_history(
                username,
                request.remote_addr
            )

            flash("Login Successful")

            return redirect("/dashboard")

        increase_failed_attempt(username)

        conn = sqlite3.connect("database.db")

        conn.row_factory = sqlite3.Row

        row = conn.execute(
            """
            SELECT failed_attempts
            FROM users
            WHERE username=?
            """,
            (username,)
        ).fetchone()

        conn.close()

        if row["failed_attempts"] >= 5:

            lock_account(username)

            flash("Account Locked after 5 failed attempts.")

        else:

            flash("Incorrect Password")

        return redirect("/login")

    return render_template("login.html")
    
    
    # ------------------------------------
# Dashboard
# ------------------------------------

@app.route("/dashboard")
def dashboard():

    if "user" not in session:

        flash("Please login first.")

        return redirect("/login")

    return render_template(
        "dashboard.html",
        username=session["user"]
    )


# ------------------------------------
# Admin Panel
# ------------------------------------

@app.route("/admin")
def admin():

    if "user" not in session:

        flash("Please login first.")

        return redirect("/login")

    if session["user"] != "admin":

        flash("Access Denied!")

        return redirect("/dashboard")

    users = get_all_users()

    return render_template(
        "admin.html",
        users=users
    )


# ------------------------------------
# Logout
# ------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully.")

    return redirect("/")


# ------------------------------------
# 404 Error Page
# ------------------------------------

@app.errorhandler(404)
def page_not_found(error):

    return render_template("404.html"), 404


# ------------------------------------
# Run Application
# ------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True
    )