from src.database.mongo import db
from bson import ObjectId

class JobDraftRepository:
    def __init__(self):
        self.col = db["job_drafts"]

    def create_draft(self, draft_data):
        return self.col.insert_one(draft_data)

    def get_drafts_by_employer(self, employer_id):
        return list(self.col.find({"employer_id": employer_id}).sort("created_at", -1))

    def delete_draft(self, draft_id):
        return self.col.delete_one({"_id": ObjectId(draft_id)})
    
    def get_draft_by_id(self, draft_id):
        return self.col.find_one({"_id": ObjectId(draft_id)})

    def update_draft(self, draft_id, update_data):
        return self.col.update_one({"_id": ObjectId(draft_id)}, {"$set": update_data})

    def delete_draft(self, draft_id):
        return self.col.delete_one({"_id": ObjectId(draft_id)})