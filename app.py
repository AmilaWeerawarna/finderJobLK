
# app.py
import os

from flask import Flask, flash, render_template, request, session, redirect, url_for
from config import Config
from src.repositories.job_post_repository import JobPostRepository
from src.repositories.user_repository import UserRepository
from src.services.message_service import MessageService
from src.controllers.auth_controller import auth_bp
from src.controllers.match_controller import match_bp
from src.controllers.profile_controller import profile_bp
from src.controllers.wishlist_controller import wishlist_bp
from src.controllers.history_controller import history_bp


from src.controllers.employer_controller import employer_bp
from src.controllers.admin_controller import admin_bp

from src.extensions import mail
from src.utils.decorators import (
    login_required,
    employer_required,
    admin_required
)

from apscheduler.schedulers.background import BackgroundScheduler
from src.services.job_service import JobService

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# REQUIRED
mail.init_app(app)

# Cookie security
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax"
)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(match_bp)

app.register_blueprint(profile_bp)
app.register_blueprint(wishlist_bp)
app.register_blueprint(history_bp)


app.register_blueprint(employer_bp)
app.register_blueprint(admin_bp)



# -------------------------------------------------
# SHARED HOME (GUEST + JOBSEEKER)
# -------------------------------------------------
@app.route("/")
def home():
    role = session.get("role")

    # Employers & Admins should not access homepage
    if role == "employer":
        return redirect(url_for("employer_dashboard")) 
    if role == "admin":
        return redirect(url_for("admin_dashboard"))   

    
    job_repo = JobPostRepository()
    user_repo = UserRepository()

    jobs_count = job_repo.get_active_jobs_count()
    employers_count = user_repo.get_user_count_by_role("employer")
    seekers_count = user_repo.get_job_seekers_count()

    return render_template(
        "public/home.html",
        is_logged_in="user_id" in session,
        name=session.get("user_name") or "Guest",
        email=session.get("user_email") or "Guest",
        user_id=session.get("user_id"),
        profile_image = session.get("profile_image"),
        role=role,
        jobs_count=jobs_count,           
        seekers_count=seekers_count,     
        employers_count=employers_count  
    )



# -----------------------------
# Employer Dashboard
# -----------------------------
@app.route("/employer/dashboard")
@login_required
@employer_required
def employer_dashboard():
    return render_template(
        "employer/dashboard.html",
        name=session.get("user_name"),
        user_id = session.get("user_id")
    )




# -----------------------------
# Admin Dashboard
# -----------------------------
@app.route("/admin/dashboard")
@login_required
@admin_required
def admin_dashboard():
    return render_template(
        "admin/dashboard.html",
        name=session.get("user_name"),
        user_id = session.get("user_id")
    )

# ======================
# contact page 
# =======================

@app.route('/contact', methods=['GET', 'POST'])
def contact_us():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        message_service = MessageService()
        success, response_msg = message_service.submit_contact_message(name, email, subject, message)

        if success:
            flash(response_msg, 'success')
            return redirect(url_for('contact_us'))
        else:
            flash(response_msg, 'danger')

    return render_template('contact.html')

# -----------------------------
# About Us Page
# -----------------------------
@app.route("/about")
def about():
    role = session.get("role")
    return render_template(
        "public/about.html",  
        is_logged_in="user_id" in session,
        name=session.get("user_name") or "Guest",
        profile_image=session.get("profile_image"),
        role=role
    )


# -----------------------------
# FAQ Page
# -----------------------------
@app.route("/faq")
def faq():
    role = session.get("role")
    return render_template(
        "public/faq.html",  
        is_logged_in="user_id" in session,
        name=session.get("user_name") or "Guest",
        profile_image=session.get("profile_image"),
        role=role
    )


# Custom 403 error handler
@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


# Custom 404 error handler
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

# Custom 405 error handler
@app.errorhandler(405)
def Method_Not_Allowed(error):
    return render_template("405.html"), 404

def start_scheduler():
    
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        scheduler = BackgroundScheduler()
        job_svc = JobService()
        
        
        scheduler.add_job(func=job_svc.check_all_expired_jobs, trigger="interval", hours=24)
        scheduler.start()


start_scheduler()

if __name__ == "__main__":
    app.run(debug=True)
