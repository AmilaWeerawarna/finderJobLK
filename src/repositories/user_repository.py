# src/repositories/user_repository.py
from src.database.mongo import db
from bson.objectid import ObjectId

class UserRepository:
    
    def __init__(self):
        self.col = db["users"]

    def create_user(self, user_data):
        # user_data is a dictionary
        return self.col.insert_one(user_data)

    def find_by_email(self, email):
        return self.col.find_one({"email": email})

    def find_by_id(self, user_id):
        return self.col.find_one({"_id": ObjectId(user_id)})

    def set_password(self, email, password_hash):
        return self.col.update_one({"email": email}, {"$set": {"password": password_hash}})

    def create_admin_if_not_exists(self, email, name, password_hash):
        if not self.find_by_email(email):
            self.create_user({
                "name": name,
                "email": email,
                "password": password_hash,
                "role": "admin",
                "created_at": None
            })
            return True
        return False
    
    def update_user(self, email, update_data):
        """Update user details based on email."""
        return self.col.update_one({"email": email}, {"$set": update_data})
    
    def get_user_by_id(self, user_id):
        return self.col.find_one({"_id": ObjectId(user_id)})

    def update_user_by_email(self, email, update_data):
        return self.col.update_one(
            {"email": email},
            {"$set": update_data}
        )
    
    def get_user_count_by_role(self, role):
        return self.col.count_documents({"role": role})
    
    def get_job_seekers_count(self):
        total_users = self.col.count_documents({})
        
        employers = self.col.count_documents({"role": "employer"})
        admins = self.col.count_documents({"role": "admin"})
        
        return total_users - (employers + admins)
    



