from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash,
    url_for
)

from flask_bcrypt import Bcrypt

import pyotp
import qrcode
import os
import re

from database import (
    add_user,
    get_user,
    get_user_by_email
)

from config import QR_FOLDER

bcrypt = Bcrypt()

auth = Blueprint("auth", __name__)


# -----------------------------------------
# Password Validation
# -----------------------------------------

def valid_password(password):

    if len(password) < 8:
        return False

    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"[a-z]", password):
        return False

    if not re.search(r"[0-9]", password):
        return False

    if not re.search(r"[!@#$%^&*()_+=\-]", password):
        return False

    return True


# -----------------------------------------
# Email Validation
# -----------------------------------------

def valid_email(email):

    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

    return re.match(pattern, email)


# -----------------------------------------
# Register
# -----------------------------------------

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"].strip()

        email = request.form["email"].strip()

        password = request.form["password"]

        confirm = request.form["confirm"]

        # Empty Fields
        if username == "" or email == "":

            flash("All fields are required.")

            return redirect(url_for("auth.register"))

        # Password Match
        if password != confirm:

            flash("Passwords do not match.")

            return redirect(url_for("auth.register"))

        # Password Strength
        if not valid_password(password):

            flash(
                "Password must contain at least "
                "8 characters, uppercase, lowercase,"
                " number and symbol."
            )

            return redirect(url_for("auth.register"))

        # Email Format
        if not valid_email(email):

            flash("Invalid email address.")

            return redirect(url_for("auth.register"))

        # Existing Username
        if get_user(username):

            flash("Username already exists.")

            return redirect(url_for("auth.register"))

        # Existing Email
        if get_user_by_email(email):

            flash("Email already registered.")

            return redirect(url_for("auth.register"))

        # Password Hash
        hashed_password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        # Generate 2FA Secret
        secret = pyotp.random_base32()

        # Save User
        add_user(
            username,
            email,
            hashed_password,
            secret
        )

        # Create QR Code
        totp = pyotp.TOTP(secret)

        uri = totp.provisioning_uri(
            name=email,
            issuer_name="Secure Login System"
        )

        img = qrcode.make(uri)

        img.save(
            os.path.join(
                QR_FOLDER,
                f"{username}.png"
            )
        )

        flash(
            "Registration Successful. "
            "Scan the QR Code using Google Authenticator."
        )

        return render_template(
            "setup2fa.html",
            username=username
        )

    return render_template("register.html")