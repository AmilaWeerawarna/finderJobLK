from src.database.mongo import db
from bson import ObjectId

class WishlistRepository:
    def __init__(self):
        self.col = db["wishlist"]

    def add_to_wishlist(self, user_id, job_id, score):
        self.col.update_one(
            {"user_id": user_id, "job_id": job_id},
            {
                "$set": {
                    "user_id": user_id, 
                    "job_id": job_id, 
                    "score": score 
                }
            },
            upsert=True
        )

    def remove_from_wishlist(self, user_id, job_id):
        self.col.delete_one({"user_id": user_id, "job_id": job_id})

    def is_job_wishlisted(self, user_id, job_id):
        item = self.col.find_one({"user_id": user_id, "job_id": job_id})
        return item is not None

    def get_user_wishlist_items(self, user_id):
        return list(self.col.find({"user_id": user_id}))