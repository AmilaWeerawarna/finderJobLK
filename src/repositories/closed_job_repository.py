from src.database.mongo import db
from bson import ObjectId

class ClosedJobRepository:
    def __init__(self):
        self.col = db["closed_jobs"]

    def insert_job(self, job_data):
        if "_id" in job_data:
            return self.col.update_one({"_id": job_data["_id"]}, {"$set": job_data}, upsert=True)
        else:
            return self.col.insert_one(job_data)

    def get_jobs_by_employer(self, employer_id):
        return list(self.col.find({"employer_id": str(employer_id)}).sort("end_date", -1))
        
    def get_job_by_id(self, job_id):
        return self.col.find_one({"_id": ObjectId(job_id)})

    def delete_job(self, job_id):
        return self.col.delete_one({"_id": ObjectId(job_id)})