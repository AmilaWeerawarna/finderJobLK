from datetime import datetime

from bson import ObjectId
from werkzeug.security import generate_password_hash

from src.repositories.user_repository import UserRepository
from src.repositories.admin_repository import AdminRepository
from src.utils.image_helper import compress_and_save_image

class AdminService:
    def __init__(self):
        self.admin_repo = AdminRepository()
        self.user_repo = UserRepository()

    def get_dashboard_stats(self):
        from src.database.mongo import db

        all_jobs = db["job_posts"].count_documents({})
        employers = self.user_repo.col.count_documents({"role": "employer"})
        job_seekers = self.user_repo.col.count_documents({"role": {"$in": ["job_seeker", "jobseeker"]}})
        closed_jobs = db["closed_jobs"].count_documents({})
        draft_jobs = db["job_drafts"].count_documents({})

        stats = {
            "all_jobs": all_jobs,
            "employers": employers,
            "job_seekers": job_seekers,
            "closed_jobs": closed_jobs
        }

        # Chart Data dictionary
        chart_data = {
            "employers_count": employers,
            "job_seekers_count": job_seekers,
            "active_jobs_count": all_jobs,
            "draft_jobs_count": draft_jobs,
            "closed_jobs_count": closed_jobs
        }

        return stats, chart_data
    
    def get_all_job_seekers(self):
        users_cursor = self.user_repo.col.find({"role": {"$in": ["job_seeker", "jobseeker"]}})
        return list(users_cursor)

    def update_job_seeker(self, user_id, name, email, password, image_file=None, upload_folder=None):
        update_data = {
            "name": name,
            "email": email
        }
        
        if password and password.strip() != "":
            update_data["password"] = generate_password_hash(password)
            
        if image_file and image_file.filename != "" and upload_folder:
            new_image_name = compress_and_save_image(image_file, upload_folder, prefix=f"js_{user_id}")
            if new_image_name:
                update_data["profile_image"] = new_image_name
                
        try:
            self.user_repo.col.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
            return True, "User updated successfully."
        except Exception as e:
            return False, "Error updating user."

    def add_job_seeker(self, name, email, password, image_file=None, upload_folder=None):
        
        if self.user_repo.find_by_email(email):
            return False, "This email is already registered."

        hashed_password = generate_password_hash(password)
        
        new_user = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "role": "jobseeker",  
            "status": "active",
            "profile_image": "default_user.png",
            "created_at": datetime.utcnow()
        }

        if image_file and image_file.filename != "" and upload_folder:
            prefix = email.split('@')[0]
            new_image_name = compress_and_save_image(image_file, upload_folder, prefix=f"js_{prefix}")
            if new_image_name:
                new_user["profile_image"] = new_image_name
        
        self.user_repo.create_user(new_user)
        return True, "Job Seeker added successfully."

    def delete_job_seeker(self, user_id):
        try:
            self.user_repo.col.delete_one({"_id": ObjectId(user_id)})
            return True, "User deleted successfully."
        except Exception as e:
            return False, "Error deleting user."
        
    def get_employers_by_status(self, status):
        employers = self.user_repo.col.find({
            "role": "employer", 
            "status": status
        })
        return list(employers)
    
    def get_employer_by_id(self, employer_id):
        from bson import ObjectId
        try:
            return self.user_repo.col.find_one({"_id": ObjectId(employer_id), "role": "employer"})
        except:
            return None
        
    def update_employer_status(self, employer_id, action):
        """Employer ගේ Status එක (Verify/Reject) වෙනස් කිරීම"""
        from bson import ObjectId
        
        status_map = {
            "verify": "active",  
            "reject": "rejected" 
        }
        
        new_status = status_map.get(action)
        if not new_status:
            return False, "Invalid action."
            
        try:
            self.user_repo.col.update_one(
                {"_id": ObjectId(employer_id)},
                {"$set": {"status": new_status}}
            )
            msg = "Employer verified successfully." if action == "verify" else "Employer rejected successfully."
            return True, msg
        except Exception as e:
            return False, "Error updating status."
        
    def get_jobs_by_employer(self, employer_id):
        from src.database.mongo import db
        return list(db["job_posts"].find({"employer_id": str(employer_id)}))

    def update_employer_by_admin(self, employer_id, name, email, company_name, phone, city, website, image_file=None, upload_folder=None):
        from bson import ObjectId
        from src.utils.image_helper import compress_and_save_image

        update_data = {
            "name": name,
            "email": email,
            "company_name": company_name,
            "phone": phone,
            "city": city,
            "website": website
        }


        if image_file and image_file.filename != "" and upload_folder:
            new_image = compress_and_save_image(image_file, upload_folder, prefix=f"emp_{employer_id}")
            if new_image:
                update_data["profile_image"] = new_image

        try:
            self.user_repo.col.update_one({"_id": ObjectId(employer_id)}, {"$set": update_data})
            return True, "Employer updated successfully."
        except Exception as e:
            return False, "Error updating employer."
        

    def add_employer_by_admin(self, name, email, company_name, phone, city, website, password, image_file=None, upload_folder=None):

        from werkzeug.security import generate_password_hash
        from datetime import datetime
        from src.utils.image_helper import compress_and_save_image


        if self.user_repo.find_by_email(email):
            return False, "This email is already registered."

        hashed_password = generate_password_hash(password)

        new_employer = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "role": "employer",
            "status": "active",
            "company_name": company_name,
            "phone": phone,
            "city": city,
            "website": website,
            "profile_image": "default_user.png",
            "created_at": datetime.utcnow()
        }

        if image_file and image_file.filename != "" and upload_folder:
            prefix = email.split('@')[0]
            new_image_name = compress_and_save_image(image_file, upload_folder, prefix=f"emp_{prefix}")
            if new_image_name:
                new_employer["profile_image"] = new_image_name

        self.user_repo.create_user(new_employer)
        return True, "Employer added successfully."
    
    def delete_employer_and_jobs(self, employer_id):
        from bson import ObjectId
        from src.database.mongo import db

        try:
            
            self.user_repo.col.delete_one({"_id": ObjectId(employer_id)})

            
            emp_id_str = str(employer_id)
            db["job_posts"].delete_many({"employer_id": emp_id_str})
            db["job_drafts"].delete_many({"employer_id": emp_id_str})
            db["closed_jobs"].delete_many({"employer_id": emp_id_str})

            return True, "Employer and all related job posts deleted successfully."
        except Exception as e:
            return False, "Error deleting employer."