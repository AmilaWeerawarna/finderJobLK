from src.database.mongo import db
from datetime import datetime

class HistoryRepository:
    def __init__(self):
        self.col = db["history"]

    def add_to_history(self, user_id, job_id, score):
        self.col.update_one(
            {"user_id": user_id, "job_id": job_id},
            {
                "$set": {
                    "user_id": user_id,
                    "job_id": job_id,
                    "score": score,
                    "viewed_at": datetime.utcnow()
                }
            },
            upsert=True
        )

    def get_user_history(self, user_id):
        return list(self.col.find({"user_id": user_id}).sort("viewed_at", -1))

    def remove_from_history(self, user_id, job_id):
        self.col.delete_one({"user_id": user_id, "job_id": job_id})