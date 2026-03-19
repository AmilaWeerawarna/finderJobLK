# src/controllers/auth_controller.py
from flask import Blueprint, render_template, request, redirect, session, flash, abort
from src.services.auth_service import AuthService

from src.utils.token import generate_token, verify_token
from src.utils.email_service import send_reset_email
from src.repositories.user_repository import UserRepository
from werkzeug.security import generate_password_hash


auth_bp = Blueprint("auth", __name__)
auth_service = AuthService()

user_repo = UserRepository()


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        role = request.form.get("role", "jobseeker")
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        extra = None
        if role == "employer":
            extra = {
                "company_name": request.form.get("company_name"),
                "phone": request.form.get("phone"),
                "city": request.form.get("city"),
                "website": request.form.get("website"),
            }

        user, error = auth_service.register_user(name, email, password, role, extra)
        if error:
            flash(error, "danger")
            return render_template("auth/register.html")
        flash("Registered successfully. Please login.", "success")
        return redirect("/login")
        
    return render_template("auth/register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # If already logged in, redirect to proper area
    if "user_email" in session:
        return redirect_after_login(session.get("role"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user, error = auth_service.login_user(email, password)
        if error:
            flash(error, "danger")
            return render_template("auth/login.html")

        # store minimal session data
        session["user_email"] = user["email"]
        session["role"] = user["role"]
        session["profile_image"] = user.get("profile_image", "default_user.png")
        # optionally store user id or name
        session["user_name"] = user.get("name")
        session["user_id"] = str(user["_id"])

        return redirect_after_login(user["role"])

    return render_template("auth/login.html")


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        user = user_repo.find_by_email(email)

        # Always show same message (security)
        if user:
            token = generate_token(email)
            send_reset_email(email, token)

        flash("If this email exists, a reset link has been sent.", "info")
        return redirect("/login")

    return render_template("auth/forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    result = verify_token(token)

    if result is None:
        abort(403)   # uses your existing 403.html

    if result == "expired":
        return render_template("token_expired.html")

    email = result  # valid token

    if request.method == "POST":
        new_password = request.form.get("password")
        hashed = generate_password_hash(new_password)
        user_repo.set_password(email, hashed)

        flash("Password reset successful. Please login.", "success")
        return redirect("/login")

    return render_template("auth/reset_password.html")



@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect("/login")


def redirect_after_login(role):
    if role == "employer":
        return redirect("/employer/dashboard")
    elif role == "admin":
        return redirect("/admin/dashboard")
    else:
        return redirect("/")

