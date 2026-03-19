from datetime import datetime
from bson import ObjectId
from src.repositories.job_draft_repository import JobDraftRepository
from src.repositories.job_post_repository import JobPostRepository
from src.repositories.closed_job_repository import ClosedJobRepository
from src.utils.image_helper import compress_and_save_image
from src.utils.deep_embedder import DeepEmbedder
from src.repositories.application_repository import ApplicationRepository

class JobService:
    def __init__(self):
        self.draft_repo = JobDraftRepository()
        self.job_repo = JobPostRepository()
        self.closed_repo = ClosedJobRepository()
        self.embedder = DeepEmbedder()
        self.app_repo = ApplicationRepository()

    def get_job_details(self, job_id: str):
        job = self.job_repo.get_job_by_id(job_id) 
        if not job:
            return None
        
        job['job_id'] = str(job['_id'])
        
        for key, value in job.items():
            if value == "NA":
                job[key] = "Not Specified"
        
        return job

    def get_employer_drafts(self, employer_id):
        return self.draft_repo.get_drafts_by_employer(employer_id)
        
    def get_draft_by_id(self, draft_id):
        return self.draft_repo.get_draft_by_id(draft_id)

    def delete_draft(self, draft_id):
        return self.draft_repo.delete_draft(draft_id)

    def get_closed_jobs(self, employer_id):
        jobs = self.closed_repo.get_jobs_by_employer(employer_id)
        for j in jobs:
            j['job_id'] = str(j['_id'])
        return jobs
    
    def get_closed_job_by_id(self, job_id):
        return self.closed_repo.get_job_by_id(job_id)

    def reactivate_closed_job(self, employer_id, job_id, new_end_date):
        job = self.closed_repo.get_job_by_id(job_id)
        
        if job and str(job.get("employer_id")) == str(employer_id):
            job["end_date"] = new_end_date
            job["status"] = "Active"
            job["updated_at"] = datetime.utcnow()
            
            self.job_repo.create_job_post(job)
            self.closed_repo.delete_job(job_id)
            return True
        return False

    def handle_job_submission(self, employer_id, form_data, action, image_file, upload_folder):
        draft_id = form_data.get("draft_id")
        closed_job_id = form_data.get("closed_job_id")
        active_job_id = form_data.get("active_job_id") 

        from bson import ObjectId

        existing_job = None
        if draft_id:
            existing_job = self.draft_repo.get_draft_by_id(draft_id)
        elif closed_job_id:
            existing_job = self.closed_repo.get_job_by_id(closed_job_id)
        elif active_job_id: 
            existing_job = self.job_repo.col.find_one({"_id": ObjectId(active_job_id)})

        job_data = {
            "employer_id": employer_id,
            "job_title": form_data.get("job_title"),
            "company_name": form_data.get("company_name"),
            "location": form_data.get("location"),
            "start_date": form_data.get("start_date"),
            "end_date": form_data.get("end_date"),
            "salary": form_data.get("salary"),
            "employment_type": form_data.get("employment_type"),
            "category": form_data.get("category"),
            "job_duties": form_data.get("job_duties"),
            "job_requirement": form_data.get("job_requirement"),
            "skills": form_data.get("skills"),
            "updated_at": datetime.utcnow()
        }

        job_text_for_embedding = f"{job_data['job_title']} {job_data['category']} {job_data['skills']} {job_data['job_duties']} {job_data['job_requirement']}"
        embedding_array = self.embedder.encode_long_text(job_text_for_embedding)
        job_data["embedding"] = embedding_array.tolist()

        if existing_job and "job_image" in existing_job:
            job_data["job_image"] = existing_job["job_image"]


        if not draft_id and not closed_job_id and not active_job_id:
            job_data["created_at"] = datetime.utcnow()


        if closed_job_id:
            job_data["_id"] = ObjectId(closed_job_id)
        elif draft_id:
            job_data["_id"] = ObjectId(draft_id)
        elif active_job_id:
            job_data["_id"] = ObjectId(active_job_id)


        if image_file and upload_folder:
            new_image = compress_and_save_image(image_file, upload_folder, prefix=f"job_{employer_id}")
            if new_image:
                job_data["job_image"] = new_image

        if action == "save":
            job_data["status"] = "Active"
            self.job_repo.create_job_post(job_data) 
            if draft_id:
                self.draft_repo.delete_draft(draft_id)
            if closed_job_id:
                self.closed_repo.delete_job(closed_job_id)
            return True, "Job post published successfully!"
            
        elif action == "draft":
            job_data["status"] = "Draft"
            if draft_id:
                self.draft_repo.update_draft(draft_id, job_data)
                return True, "Draft updated successfully."
            elif closed_job_id:
                self.draft_repo.create_draft(job_data)
                self.closed_repo.delete_job(closed_job_id)
                return True, "Closed job moved to drafts successfully."
            elif active_job_id:
                self.draft_repo.create_draft(job_data)
                self.job_repo.col.delete_one({"_id": ObjectId(active_job_id)}) 
                return True, "Active job moved to drafts successfully."
            else:
                self.draft_repo.create_draft(job_data)
                return True, "Job saved to drafts successfully."

        return False, "Invalid action specified."


    def check_all_expired_jobs(self):
        today_str = datetime.now().strftime('%Y-%m-%d')
        active_jobs = self.job_repo.col.find({"end_date": {"$lt": today_str}})
        
        for job in active_jobs:
            job["status"] = "Closed"
            self.closed_repo.insert_job(job)
            self.job_repo.delete_job(str(job["_id"]))

    def get_employer_applications(self, employer_id):
        employer_jobs = self.job_repo.col.find({"employer_id": str(employer_id)})
        job_map = {str(job["_id"]): job.get("job_title", "Unknown Job") for job in employer_jobs}
        job_ids = list(job_map.keys())

        if not job_ids:
            return []

        applications = self.app_repo.get_applications_by_job_ids(job_ids)
        for app in applications:
            app["job_title"] = job_map.get(app["job_id"], "Unknown Job")
            
        return applications


    def get_application_cv_path(self, app_id):
        app = self.app_repo.get_application_by_id(app_id)
        return app.get("cv_path") if app else None
    
    def delete_application(self, app_id):
        return self.app_repo.delete_application(app_id)
    
    def get_employer_active_jobs_with_stats(self, employer_id):
        active_jobs = list(self.job_repo.col.find({"employer_id": str(employer_id)}).sort("_id", -1))
        
        for job in active_jobs:
            job_id_str = str(job["_id"])
            app_count = self.app_repo.col.count_documents({"job_id": job_id_str})
            job["applicant_count"] = app_count
            
        return active_jobs
    
    def delete_active_job(self, job_id):
        from bson import ObjectId
        return self.job_repo.col.delete_one({"_id": ObjectId(job_id)})