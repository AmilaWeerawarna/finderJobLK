from src.database.mongo import db

class AdminRepository:
    def get_total_job_posts(self):
        return db["job_posts"].count_documents({})

    def get_total_employers(self):
        return db["users"].count_documents({"role": "employer"})

    def get_total_job_seekers(self):
        return db["users"].count_documents({"role": {"$in": ["job_seeker", "jobseeker"]}})

    def get_total_closed_jobs(self):
        return db["closed_jobs"].count_documents({})