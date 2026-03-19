from bson import ObjectId
from flask import Blueprint, current_app, render_template, request, session, redirect, url_for, flash
from src.services.message_service import MessageService
from src.services.admin_service import AdminService
from src.repositories.message_repository import MessageRepository

admin_bp = Blueprint("admin", __name__)
admin_service = AdminService()

# 1. Context Processor
# Injects the unread messages count into all HTML templates rendered by this blueprint.
@admin_bp.context_processor
def inject_unread_count():
    if session.get("role") == "admin":
        msg_service = MessageService()
        count = msg_service.get_unread_count()
        return dict(unread_count=count)
    return dict(unread_count=0)

@admin_bp.route("/admin/dashboard")
def admin_dashboard():
    # Check if the current user has admin privileges
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))

    # Fetch dashboard statistics and chart data from the service layer (MVC pattern)
    stats, chart_data = admin_service.get_dashboard_stats()

    # Pass the fetched data to the view
    return render_template("admin/dashboard.html", stats=stats, chart_data=chart_data)

@admin_bp.route("/admin/manage_job_seekers", methods=["GET", "POST"])
def manage_job_seekers():
    if session.get("role") != "admin":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        action = request.form.get("action")
        user_id = request.form.get("user_id")
        name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Retrieve the uploaded profile image from the form data
        image_file = request.files.get("profile_image")
        upload_folder = current_app.config.get("UPLOAD_FOLDER_PROFILS", "static/profile_img")
        
        if action == "update":
            # Pass the image and other details to the service layer for updating
            success, message = admin_service.update_job_seeker(user_id, name, email, password, image_file, upload_folder)
        else:
            # Pass the image and details to add a new job seeker
            success, message = admin_service.add_job_seeker(name, email, password, image_file, upload_folder)
            
        if success:
            flash(message, "success")
        else:
            flash(message, "danger")
            
        return redirect(url_for("admin.manage_job_seekers"))

    job_seekers = admin_service.get_all_job_seekers()
    return render_template("admin/manage_job_seekers.html", users=job_seekers)


# Route for deleting a job seeker
@admin_bp.route("/admin/delete_job_seeker/<user_id>", methods=["POST"])
def delete_job_seeker(user_id):
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))
        
    success, message = admin_service.delete_job_seeker(user_id)
    if success:
        flash(message, "success")
    else:
        flash(message, "danger")
        
    return redirect(url_for("admin.manage_job_seekers"))


@admin_bp.route("/admin/manage_employers")
def manage_employers():
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))
    return redirect(url_for("admin.pending_employers"))

# Route for displaying employers pending verification
@admin_bp.route("/admin/manage_employers/pending")
def pending_employers():
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))
        
    # Fetch the list of employers with a 'PENDING' status
    pending_list = admin_service.get_employers_by_status("PENDING")
    
    return render_template("admin/manage_employers_pending.html", employers=pending_list)

# Route to view the details of a specific pending employer
@admin_bp.route("/admin/manage_employers/pending/<employer_id>")
def pending_employer_detail(employer_id):
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))
        
    employer = admin_service.get_employer_by_id(employer_id)
    if not employer:
        flash("Employer not found.", "danger")
        return redirect(url_for("admin.pending_employers"))
        
    return render_template("admin/manage_employer_detail.html", employer=employer)

# Handle the action to verify or reject an employer
@admin_bp.route("/admin/manage_employers/action", methods=["POST"])
def employer_action():
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))
        
    employer_id = request.form.get("employer_id")
    action = request.form.get("action") # Expected values: 'verify' or 'reject'
    
    success, message = admin_service.update_employer_status(employer_id, action)
    if success:
        flash(message, "success")
    else:
        flash(message, "danger")
        
    # Redirect back to the pending employers list after the action is processed
    return redirect(url_for("admin.pending_employers"))


# Route for displaying verified (active) employers
@admin_bp.route("/admin/manage_employers/verified")
def verified_employers():
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))
        
    # Fetch the list of verified employers (status: 'active')
    verified_list = admin_service.get_employers_by_status("active")
    
    return render_template("admin/manage_employers_verified.html", employers=verified_list)

# Route for displaying rejected employers
@admin_bp.route("/admin/manage_employers/rejected")
def rejected_employers():
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))
        
    # Fetch the list of employers with a 'rejected' status
    rejected_list = admin_service.get_employers_by_status("rejected")
    
    return render_template("admin/manage_employers_rejected.html", employers=rejected_list)


@admin_bp.route("/admin/manage_employers/verified/<employer_id>")
def verified_employer_detail(employer_id):
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))
        
    employer = admin_service.get_employer_by_id(employer_id)
    if not employer:
        flash("Employer not found.", "danger")
        return redirect(url_for("admin.verified_employers"))
        
    # Fetch all job posts associated with this specific employer
    employer_jobs = admin_service.get_jobs_by_employer(employer_id)
        
    return render_template("admin/manage_employer_verified_detail.html", employer=employer, jobs=employer_jobs)

# Handle updating the details of a verified employer
@admin_bp.route("/admin/manage_employers/verified/update", methods=["POST"])
def update_verified_employer():
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))

    employer_id = request.form.get("employer_id")
    name = request.form.get("full_name")
    email = request.form.get("email")
    company_name = request.form.get("company_name")
    phone = request.form.get("phone")
    city = request.form.get("city")
    website = request.form.get("website")

    image_file = request.files.get("profile_image")
    upload_folder = current_app.config.get("UPLOAD_FOLDER_PROFILS", "static/profile_img")

    success, msg = admin_service.update_employer_by_admin(
        employer_id, name, email, company_name, phone, city, website, image_file, upload_folder
    )

    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")

    return redirect(f"/admin/manage_employers/verified/{employer_id}")

# Route to display the form for adding a new job post for an employer
@admin_bp.route("/admin/manage_employers/verified/<employer_id>/add_job")
def admin_add_job(employer_id):
    if session.get("role") != "admin": return redirect(url_for("auth.login"))
    employer = admin_service.get_employer_by_id(employer_id)
    return render_template("admin/manage_employer_job_form.html", employer_id=employer_id, company_name=employer.get('company_name', ''), edit_job=None)

# Route to display the form for editing an existing job post
@admin_bp.route("/admin/manage_employers/verified/<employer_id>/edit_job/<job_id>")
def admin_edit_job(employer_id, job_id):
    if session.get("role") != "admin": return redirect(url_for("auth.login"))
    
    # Fetch the specific job details from the database
    from src.database.mongo import db
    job = db["job_posts"].find_one({"_id": ObjectId(job_id)})
    return render_template("admin/manage_employer_job_form.html", employer_id=employer_id, company_name="", edit_job=job)

# Handle form submission for both adding and editing a job post
@admin_bp.route("/admin/manage_employers/verified/job_action", methods=["POST"])
def admin_job_action():
    if session.get("role") != "admin": return redirect(url_for("auth.login"))
    
    employer_id = request.form.get("employer_id")
    job_id = request.form.get("job_id")
    image_file = request.files.get("job_image")
    upload_folder = current_app.config.get("UPLOAD_FOLDER_JOBS", "static/company_logos")

    # Use job_service.handle_job_submission to save the job (works for both creation and updates)
    from src.services.job_service import JobService
    job_service = JobService()
    
    # Pass the job_id as closed_job_id in the form data
    # (Trick to update an existing active job using the same service function)
    form_data = dict(request.form)
    if job_id:
        form_data["closed_job_id"] = job_id 

    success, message = job_service.handle_job_submission(
        employer_id=employer_id,
        form_data=form_data,
        action="save",
        image_file=image_file,
        upload_folder=upload_folder
    )

    flash(message, "success" if success else "danger")
    return redirect(f"/admin/manage_employers/verified/{employer_id}")

# Handle the deletion of a specific job post
@admin_bp.route("/admin/manage_employers/verified/delete_job/<job_id>", methods=["POST"])
def admin_delete_job(job_id):
    if session.get("role") != "admin": return redirect(url_for("auth.login"))
    employer_id = request.form.get("employer_id")
    
    from src.database.mongo import db
    db["job_posts"].delete_one({"_id": ObjectId(job_id)})
    
    flash("Job post deleted successfully.", "success")
    return redirect(f"/admin/manage_employers/verified/{employer_id}")

# Route to manually add a new employer from the admin panel
@admin_bp.route("/admin/manage_employers/add", methods=["GET", "POST"])
def admin_add_employer():
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")
        company_name = request.form.get("company_name")
        phone = request.form.get("phone")
        city = request.form.get("city")
        website = request.form.get("website")

        image_file = request.files.get("profile_image")
        upload_folder = current_app.config.get("UPLOAD_FOLDER_PROFILS", "static/profile_img")

        success, message = admin_service.add_employer_by_admin(
            name, email, company_name, phone, city, website, password, image_file, upload_folder
        )

        if success:
            flash(message, "success")
            return redirect(url_for("admin.verified_employers"))
        else:
            flash(message, "danger")

    return render_template("admin/manage_employer_add.html")

# Handle the complete deletion of an employer and their associated data
@admin_bp.route("/admin/manage_employers/delete/<employer_id>", methods=["POST"])
def admin_delete_employer(employer_id):
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))

    success, message = admin_service.delete_employer_and_jobs(employer_id)
    if success:
        flash(message, "success")
    else:
        flash(message, "danger")

    # Redirect back to the verified employers list after deletion
    return redirect(url_for("admin.verified_employers"))

# Route to view all contact messages
@admin_bp.route("/admin/messages")
def admin_messages():
    if session.get("role") != "admin":
        return redirect(url_for("auth.login"))
        
    message_service = MessageService()
    all_messages = message_service.get_all_messages()
    
    # Mark all unread messages as 'read' as soon as the messages page is opened
    message_service.mark_all_as_read()
    
    return render_template("admin/messages.html", messages=all_messages)

# Route to delete a specific message
@admin_bp.route("/admin/delete_message/<msg_id>")
# TODO: Uncomment the @admin_required decorator here to enforce authentication
# @admin_required  
def delete_message(msg_id):
    # Initialize the MessageRepository
    msg_repo = MessageRepository() 
    
    # Delete the message using the repository
    if msg_repo.delete_message(msg_id):
        flash("Message deleted successfully.", "success")
    else:
        flash("Failed to delete message.", "danger")
        
    return redirect("/admin/messages")