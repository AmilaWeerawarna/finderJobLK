import os
from flask import Blueprint, current_app, flash, render_template, request, session, redirect, url_for
from werkzeug.utils import secure_filename

from src.repositories.history_repository import HistoryRepository
from src.repositories.wishlist_repository import WishlistRepository
from src.repositories.job_post_repository import JobPostRepository
from src.repositories.application_repository import ApplicationRepository
from src.repositories.user_repository import UserRepository # අලුත් Repo එක
from src.services.job_service import JobService
from src.utils.decorators import login_required

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    user_repo = UserRepository()
    user = user_repo.get_user_by_id(user_id)
    
    wishlist_repo = WishlistRepository()
    job_repo = JobPostRepository()
    history_repo = HistoryRepository() 

    # --- Wishlist Data ---
    wishlist_items = wishlist_repo.get_user_wishlist_items(user_id)
    wishlist_score_map = {item['job_id']: item.get('score', 0) for item in wishlist_items}
    wishlist_ids = list(wishlist_score_map.keys())
    wishlist_jobs = job_repo.get_jobs_by_ids(wishlist_ids)
    for job in wishlist_jobs:
        job['score'] = wishlist_score_map.get(job['job_id'], 0)

    # --- History Data ---
    history_items = history_repo.get_user_history(user_id)
    history_ids = [item['job_id'] for item in history_items]
    raw_history_jobs = job_repo.get_jobs_by_ids(history_ids)
    job_map = {job['job_id']: job for job in raw_history_jobs}
    
    final_history_jobs = []
    for item in history_items:
        job_id = item['job_id']
        if job_id in job_map:
            job_obj = job_map[job_id]
            job_obj['score'] = item.get('score', 0)
            final_history_jobs.append(job_obj)

    # --- My Applications Data ---
    app_repo = ApplicationRepository()
    job_service = JobService()
    
    user_apps = app_repo.get_applications_by_user_id(user_id)
    
    applied_jobs = []
    for app in user_apps:
        job_details = job_service.get_job_details(app['job_id'])
        if job_details:
            job_details['score'] = app.get('score', 0)
            job_details['applied_at'] = app.get('applied_at')
            job_details['status'] = app.get('status', 'Pending')
            applied_jobs.append(job_details)

    return render_template(
        "public/profile.html", 
        user=user, 
        wishlist_jobs=wishlist_jobs,
        history_jobs=final_history_jobs,
        applied_jobs=applied_jobs 
    )

@profile_bp.route("/profile/update", methods=["POST"])
@login_required
def update_profile():
    user_email = session["user_email"]
    
    name = request.form.get("name")
    phone = request.form.get("phone")
    bio = request.form.get("bio")

    update_data = {
        "name": name,
        "phone": phone,
        "bio": bio
    }

    if 'profile_image' in request.files:
        file = request.files['profile_image']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            unique_filename = f"{user_email}_{filename}"
            
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER_PROFILS'], unique_filename)
            file.save(file_path)
            
            update_data["profile_image"] = unique_filename
            session["profile_image"] = unique_filename 

    user_repo = UserRepository()
    user_repo.update_user_by_email(user_email, update_data)

    if name:
        session["user_name"] = name

    flash("Profile updated successfully!", "success")
    return redirect("/profile")