import os

from flask import Blueprint, render_template, request, session, redirect, flash, current_app, url_for

from src.services.profile_service import ProfileService
from src.services.job_service import JobService
from src.utils.decorators import employer_required
from flask import send_file

employer_bp = Blueprint("employer", __name__)

profile_service = ProfileService()
job_service = JobService()


@employer_bp.route("/employer/dashboard")
@employer_required
def dashboard():
    user_id = session.get("user_id")
    
    # Automatically check and move expired jobs to the closed jobs collection
    job_service.check_all_expired_jobs()
    
    current_user = profile_service.get_employer_profile(user_id)
    user_drafts = job_service.get_employer_drafts(user_id)
    closed_jobs = job_service.get_closed_jobs(user_id)
    applications = job_service.get_employer_applications(user_id)
    active_jobs = job_service.get_employer_active_jobs_with_stats(user_id)
    
    # Prepare data for the Top Stats Cards
    total_active = len(active_jobs)
    total_apps = len(applications)
    
    # Replace hardcoded 0 with actual dynamic counts
    shortlisted_count = len(user_drafts)  # Number of Draft Jobs
    profile_views = len(closed_jobs)      # Number of Closed Jobs
    
    return render_template("employer/dashboard.html", 
                           drafts=user_drafts, 
                           current_user=current_user, 
                           closed_jobs=closed_jobs, 
                           applications=applications, 
                           active_jobs=active_jobs,
                           total_active=total_active,
                           total_apps=total_apps,
                           shortlisted_count=shortlisted_count,
                           profile_views=profile_views)

@employer_bp.route("/employer/reactivate-job", methods=["POST"])
@employer_required
def reactivate_job():
    user_id = session.get("user_id")
    job_id = request.form.get("job_id")
    new_end_date = request.form.get("new_end_date")
    
    if job_service.reactivate_closed_job(user_id, job_id, new_end_date):
        flash("Job successfully reactivated and published!", "success")
    else:
        flash("Failed to reactivate job.", "danger")
        
    return redirect("/employer/dashboard?tab=close-job-tab")


@employer_bp.route("/employer/update-profile", methods=["POST"])
@employer_required
def update_profile():
    user_email = session.get("user_email")
    name = request.form.get("name")
    
    update_data = {
        "name": name,
        "company_name": request.form.get("company_name"),
        "phone": request.form.get("phone"),
        "city": request.form.get("city"),
        "website": request.form.get("website")
    }
    
    image_file = request.files.get("profile_image")
    upload_folder = current_app.config.get("UPLOAD_FOLDER_PROFILS", "static/profile_img")
    
    new_image = profile_service.update_employer_profile(user_email, update_data, image_file, upload_folder)
    
    # Update session variables if profile information was changed
    if name:
        session["user_name"] = name
    if new_image:
        session["profile_image"] = new_image
        
    flash("Profile updated successfully!", "success")
    return redirect("/employer/dashboard")

@employer_bp.route("/employer/add-job", methods=["POST"])
@employer_required
def add_job():
    user_id = session.get("user_id")
    
    # Check if the employer's status is "active" before allowing job posting
    current_user = profile_service.get_employer_profile(user_id)
    if current_user.get("status", "active") != "active":
        flash("Your account is not verified yet. You cannot post jobs.", "danger")
        return redirect("/employer/dashboard")

    action = request.form.get("action") 
    image_file = request.files.get("job_image")
    upload_folder = current_app.config.get("UPLOAD_FOLDER_JOBS", "static/company_logos")

    # Handle the form submission to either save as active or as a draft
    success, message = job_service.handle_job_submission(
        employer_id=user_id,
        form_data=request.form,
        action=action,
        image_file=image_file,
        upload_folder=upload_folder
    )

    if success:
        flash(message, "success" if action == "save" else "info")
    else:
        flash(message, "danger")

    # Redirect to the add job tab if saved as a draft
    if action == "draft":
        return redirect(url_for("employer.dashboard", tab="add-job-tab"))

    return redirect("/employer/dashboard")

@employer_bp.route("/employer/edit-draft/<draft_id>")
@employer_required
def edit_draft(draft_id):
    user_id = session.get("user_id")
    
    current_user = profile_service.get_employer_profile(user_id)
    user_drafts = job_service.get_employer_drafts(user_id)
    closed_jobs = job_service.get_closed_jobs(user_id)
    applications = job_service.get_employer_applications(user_id)
    active_jobs = job_service.get_employer_active_jobs_with_stats(user_id)
    
    draft_to_edit = job_service.get_draft_by_id(draft_id)
    
    # Verify ownership of the draft
    if not draft_to_edit or str(draft_to_edit.get("employer_id")) != str(user_id):
        flash("Draft not found or unauthorized.", "danger")
        return redirect("/employer/dashboard")
        
    # Add missing dashboard statistics
    total_active = len(active_jobs)
    total_apps = len(applications)
    shortlisted_count = len(user_drafts)
    profile_views = len(closed_jobs)
        
    return render_template("employer/dashboard.html", 
                           drafts=user_drafts, 
                           closed_jobs=closed_jobs, 
                           current_user=current_user,
                           applications=applications,
                           active_jobs=active_jobs,
                           total_active=total_active,
                           total_apps=total_apps,
                           shortlisted_count=shortlisted_count,
                           profile_views=profile_views,
                           edit_draft=draft_to_edit)

@employer_bp.route("/employer/delete-draft/<draft_id>")
@employer_required
def delete_draft(draft_id):
    user_id = session.get("user_id")
    draft = job_service.get_draft_by_id(draft_id)
    
    # Check if the draft belongs to the current user before deleting
    if draft and str(draft.get("employer_id")) == str(user_id):
        job_service.delete_draft(draft_id)
        flash("Draft deleted successfully.", "success")
    else:
        flash("Failed to delete draft.", "danger")
        
    # Change: Redirect to the "Add Job Post" tab after deletion
    return redirect(url_for("employer.dashboard", tab="add-job-tab"))


@employer_bp.route("/employer/edit-closed-job/<job_id>")
@employer_required
def edit_closed_job(job_id):
    user_id = session.get("user_id")
    
    current_user = profile_service.get_employer_profile(user_id)
    user_drafts = job_service.get_employer_drafts(user_id)
    closed_jobs = job_service.get_closed_jobs(user_id)
    applications = job_service.get_employer_applications(user_id)
    active_jobs = job_service.get_employer_active_jobs_with_stats(user_id)
    
    job_to_edit = job_service.get_closed_job_by_id(job_id)
    
    # Verify ownership of the closed job
    if not job_to_edit or str(job_to_edit.get("employer_id")) != str(user_id):
        flash("Job not found or unauthorized.", "danger")
        return redirect("/employer/dashboard")
        
    # Add missing dashboard statistics
    total_active = len(active_jobs)
    total_apps = len(applications)
    shortlisted_count = len(user_drafts)
    profile_views = len(closed_jobs)
        
    return render_template("employer/dashboard.html", 
                           drafts=user_drafts, 
                           closed_jobs=closed_jobs, 
                           current_user=current_user,
                           applications=applications,
                           active_jobs=active_jobs,
                           total_active=total_active,
                           total_apps=total_apps,
                           shortlisted_count=shortlisted_count,
                           profile_views=profile_views,
                           edit_draft=job_to_edit)


# New route for downloading the applicant's CV
@employer_bp.route("/employer/download-cv/<app_id>")
@employer_required
def download_cv(app_id):
    cv_path = job_service.get_application_cv_path(app_id)
    
    if cv_path and os.path.exists(cv_path):
        return send_file(cv_path, as_attachment=True)
        
    flash("CV file not found on the server.", "danger")
    return redirect(url_for("employer.dashboard", tab="applicants-tab"))

# New route for deleting an applicant
@employer_bp.route("/employer/delete-applicant/<app_id>")
@employer_required
def delete_applicant(app_id):
    if job_service.delete_application(app_id):
        flash("Applicant deleted successfully.", "success")
    else:
        flash("Failed to delete applicant.", "danger")
        
    return redirect(url_for("employer.dashboard", tab="applicants-tab"))


@employer_bp.route("/employer/edit-active-job/<job_id>")
@employer_required
def edit_active_job(job_id):
    user_id = session.get("user_id")
    
    current_user = profile_service.get_employer_profile(user_id)
    user_drafts = job_service.get_employer_drafts(user_id)
    closed_jobs = job_service.get_closed_jobs(user_id)
    applications = job_service.get_employer_applications(user_id)
    active_jobs = job_service.get_employer_active_jobs_with_stats(user_id)
    
    job_to_edit = job_service.job_repo.get_job_by_id(job_id)
    
    # Verify ownership of the active job
    if not job_to_edit or str(job_to_edit.get("employer_id")) != str(user_id):
        flash("Job not found or unauthorized.", "danger")
        return redirect("/employer/dashboard")
        
    # Add missing dashboard statistics
    total_active = len(active_jobs)
    total_apps = len(applications)
    shortlisted_count = len(user_drafts)
    profile_views = len(closed_jobs)
        
    return render_template("employer/dashboard.html", 
                           drafts=user_drafts, 
                           closed_jobs=closed_jobs, 
                           current_user=current_user, 
                           applications=applications,
                           active_jobs=active_jobs,
                           total_active=total_active,
                           total_apps=total_apps,
                           shortlisted_count=shortlisted_count,
                           profile_views=profile_views,
                           edit_draft=job_to_edit)


# Route to delete an active job post
@employer_bp.route("/employer/delete-active-job/<job_id>")
@employer_required
def delete_active_job(job_id):
    user_id = session.get("user_id")
    job = job_service.job_repo.get_job_by_id(job_id)
    
    # Ensure the employer deleting the job is the actual owner
    if job and str(job.get("employer_id")) == str(user_id):
        job_service.delete_active_job(job_id)
        flash("Active job deleted successfully.", "success")
    else:
        flash("Failed to delete job.", "danger")
        
    return redirect("/employer/dashboard")