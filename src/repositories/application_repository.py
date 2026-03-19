from bson import ObjectId

from src.database.mongo import db

class ApplicationRepository:
    def __init__(self):
        # A new collection called "applications" is created in the database.
        self.col = db["applications"]

    def save_application(self, application_data):
        """Saving a new application in the database"""
        return self.col.insert_one(application_data)
        
    def has_user_applied(self, user_id, job_id):
        """Check if the user has applied for this job before."""
        return self.col.find_one({"user_id": user_id, "job_id": job_id}) is not None
    
    def get_applications_by_job_ids(self, job_ids):
        """Obtaining all applications related to multiple jobs from an employer (highest score first)"""
        return list(self.col.find({"job_id": {"$in": job_ids}}).sort([("score", -1), ("applied_at", -1)]))

    def get_application_by_id(self, app_id):
        """Obtaining an application using the ID (to download CV)"""
        return self.col.find_one({"_id": ObjectId(app_id)})
    
    def delete_application(self, app_id):
        from bson import ObjectId
        """Deleting an applicant from the database"""
        return self.col.delete_one({"_id": ObjectId(app_id)})
    
    def get_applications_by_user_id(self, user_id):
        """Getting all the jobs a Job Seeker has applied for"""
        return list(self.col.find({"user_id": str(user_id)}).sort("applied_at", -1))