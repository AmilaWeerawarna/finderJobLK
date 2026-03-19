from typing import Any, Dict, List
from bson import ObjectId
from src.database.mongo import db
from config import Config

class JobPostRepository:
    """Read-only repository for job posts."""

    def __init__(self):
        self.col = db[Config.JOB_POSTS_COLLECTION]

    def get_job_by_id(self, job_id: str) -> Dict[str, Any]:
        """Fetch a single job post by its ObjectId."""
        return self.col.find_one({"_id": ObjectId(job_id)})

    def get_all_job_posts(self, limit: int = 500) -> List[Dict[str, Any]]:
        """Fetch job posts (cap to keep matching fast)."""
        return list(self.col.find({}).limit(limit))
    
    def get_jobs_by_ids(self, job_ids: List[str]) -> List[Dict[str, Any]]:
        if not job_ids:
            return []
        
        object_ids = [ObjectId(jid) for jid in job_ids]
        jobs = list(self.col.find({"_id": {"$in": object_ids}}))
        
        for job in jobs:
            job['job_id'] = str(job['_id'])
            
        return jobs

    def create_job_post(self, job_data: dict):
        """Insert or Update a job post into the collection."""
        if "_id" in job_data:
            return self.col.update_one({"_id": job_data["_id"]}, {"$set": job_data}, upsert=True)
        else:
            return self.col.insert_one(job_data)
    

    def get_jobs_by_employer(self, employer_id: str) -> List[Dict[str, Any]]:
        return list(self.col.find({"employer_id": str(employer_id)}))

    def delete_job(self, job_id: str):
        return self.col.delete_one({"_id": ObjectId(job_id)})
    
    def get_active_jobs_count(self):
        return self.col.count_documents({"status": "Active"})