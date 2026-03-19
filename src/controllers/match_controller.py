import datetime
from datetime import datetime as dt
import os
import uuid

from flask import Blueprint, current_app, flash, json, jsonify, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

from src.repositories.application_repository import ApplicationRepository
from src.repositories.history_repository import HistoryRepository
from src.repositories.wishlist_repository import WishlistRepository
from src.services.deep_match_service import DeepMatchService

from config import Config
from src.utils.pdf_extractor import extract_text_from_pdf

from src.services.job_service import JobService # අලුත් service එක import කරන්න


match_bp = Blueprint("match", __name__)
ALLOWED_EXTENSIONS = {"pdf"}

def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@match_bp.route("/match", methods=["GET", "POST"])
def match_jobs():
    if request.method == "POST":
        cv_file = request.files.get("cv_pdf")

        if cv_file and cv_file.filename != "" and _allowed_file(cv_file.filename):
            
            if "user_id" in session:
                user_id = str(session["user_id"])
            else:
                if "guest_id" not in session:
                    session["guest_id"] = f"guest_{uuid.uuid4().hex[:8]}"
                user_id = session["guest_id"]

            uploads_dir = current_app.config.get("UPLOAD_FOLDER", "uploads")
            user_upload_dir = os.path.join(uploads_dir, str(user_id))
            os.makedirs(user_upload_dir, exist_ok=True)

            filename = secure_filename(cv_file.filename)
            cv_path = os.path.join(user_upload_dir, filename)
            cv_file.save(cv_path)

            service = DeepMatchService()
            try:
                profile_dict, results, meta = service.match(
                    cv_pdf_path=cv_path,
                    top_k=10
                )

                result_data = {
                    'results': results,
                    'meta': meta,
                    'cv_path': cv_path,
                    'skills': profile_dict.get("skills", []),
                    'education': profile_dict.get("education", []),
                    'experience': profile_dict.get("experience", []) # අලුතින් එක් කළ පේළිය
                }
                
                json_path = os.path.join(user_upload_dir, "last_match.json")
                with open(json_path, 'w') as f:
                    json.dump(result_data, f)

                session['match_result_path'] = json_path
                return redirect(url_for("match.match_jobs"))

            except Exception as e:
                print(f"Error: {e}") 
                flash("AI job matching failed.")
                return redirect(url_for("home"))
        else:
            flash("Please upload a valid PDF CV.")
            return redirect(url_for("home"))

    # GET Request
    json_path = session.get('match_result_path')

    if not json_path or not os.path.exists(json_path):
        return redirect(url_for("home"))
    
    with open(json_path, 'r') as f:
        data = json.load(f)

    return render_template(
        "public/match_results.html",
        name=session.get("user_name"),
        saved_cv_path=data['cv_path'],
        extracted_skills=data.get('skills', []),
        extracted_education=data.get('education', []),
        extracted_experience=data.get('experience', []),
        meta=data['meta'],
        results=data['results'],
    )



@match_bp.route("/job/<job_id>")
def job_details(job_id):
    service = JobService()
    job = service.get_job_details(job_id)
    
    score = request.args.get('score', 0)
    
    if not job:
        return render_template("404.html"), 404
        
    user_id = session.get("user_id")
    user_name = session.get("user_name", "")
    user_email = session.get("user_email", "")
    
    is_wishlisted = False
    cv_filename = None
    has_applied = False 
    
    if user_id:
        wishlist_repo = WishlistRepository()
        is_wishlisted = wishlist_repo.is_job_wishlisted(user_id, job['job_id'])
        
        history_repo = HistoryRepository()
        history_repo.add_to_history(user_id, job['job_id'], score)

        app_repo = ApplicationRepository()
        has_applied = app_repo.has_user_applied(user_id, job['job_id'])

        # පරණ Match Result එකෙන් CV එකේ නම හොයාගැනීම
        json_path = session.get('match_result_path')
        if json_path and os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    data = json.load(f)
                    cv_path = data.get('cv_path')
                    if cv_path:
                        cv_filename = os.path.basename(cv_path) 
            except Exception as e:
                print(f"Error reading CV path: {e}")

    return render_template("public/job_detail.html", job=job, score=score, is_wishlisted=is_wishlisted, 
                           cv_filename=cv_filename, user_name=user_name, user_email=user_email,
                           has_applied=has_applied)


@match_bp.route("/api/analyze-job/<job_id>")
def api_analyze_job(job_id):
    service = JobService()
    job = service.get_job_details(job_id)
    
    if not job:
        return jsonify({"error": "Job not found"}), 404

    json_path = session.get('match_result_path')
    
    if json_path and os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                
            cv_path = data.get('cv_path')
            extracted_skills = data.get('skills', [])
            extracted_education = data.get('education', [])
            extracted_experience = data.get('experience', []) 
            
            if cv_path and os.path.exists(cv_path):
                cv_text = extract_text_from_pdf(cv_path)
                
                match_service = DeepMatchService()
                analysis_result = match_service.analyze_cv_vs_job(
                    job_dict=job,
                    cv_text=cv_text,
                    extracted_skills=extracted_skills,
                    extracted_education=extracted_education,
                    extracted_experience=extracted_experience 
                )
                
                return jsonify({"success": True, "analysis": analysis_result})
        except Exception as e:
            print(f"Error in CV Analysis: {e}")
            return jsonify({"error": "Analysis failed due to server error."}), 500

    return jsonify({"error": "No CV data found. Please match your CV first."}), 400

@match_bp.route("/apply-job", methods=["POST"])
def apply_job():
    job_id = request.form.get("job_id")
    full_name = request.form.get("full_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    score = request.form.get("score", 0)
    
    try:
        clean_score = float(str(score).replace('%', '').strip()) if score else 0.0
    except ValueError:
        clean_score = 0.0
    
    user_id = session.get("user_id") or session.get("guest_id")
    
    app_repo = ApplicationRepository()
    if app_repo.has_user_applied(user_id, job_id):
        flash("You have already applied for this job.", "info")

        return redirect(url_for('match.job_details', job_id=job_id, score=score))

    json_path = session.get('match_result_path')
    cv_path = None
    
    if json_path and os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                cv_path = data.get('cv_path')
        except Exception as e:
            print(f"Error reading CV path: {e}")

    if not cv_path:
        flash("CV not found. Please upload your CV and match it before applying.", "danger")
        return redirect(url_for('match.job_details', job_id=job_id, score=score))

    from datetime import datetime as dt

    application_data = {
        "job_id": job_id,
        "user_id": user_id,
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "cv_path": cv_path,
        "score": clean_score, # 🟢 පිරිසිදු කළ Score එක
        "status": "Pending",
        "applied_at": dt.utcnow() 
    }

    try:
        app_repo.save_application(application_data)
        flash("Your application has been submitted successfully!", "success")
    except Exception as e:
        print(f"Database Save Error: {e}")
        flash("Failed to submit application. Please try again.", "danger")
        
    return redirect(url_for('match.job_details', job_id=job_id, score=score))