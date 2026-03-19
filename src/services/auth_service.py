# src/services/auth_service.py
from werkzeug.security import generate_password_hash, check_password_hash
from src.repositories.user_repository import UserRepository
from datetime import datetime

class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()

    def register_user(self, name, email, password, role, extra=None):
        # extra can store employer fields like company_name, phone, city
        if self.user_repo.find_by_email(email):
            return None, "Email already registered."

        hashed = generate_password_hash(password)
        doc = {
            "name": name,
            "email": email,
            "password": hashed,
            "role": role,
            "status": "active",
            "created_at": datetime.utcnow()
        }

        # For employer, store extra fields and status
        if role == "employer" and extra:
            doc.update({
                "company_name": extra.get("company_name"),
                "phone": extra.get("phone"),
                "city": extra.get("city"),
                "website": extra.get("website"),
                "status": "PENDING"  # admin must verify
            })

        self.user_repo.create_user(doc)
        return doc, None

    def login_user(self, email, password):
        user = self.user_repo.find_by_email(email)
        if not user:
            return None, "Email not found."
        if not check_password_hash(user["password"], password):
            return None, "Incorrect password."
        return user, None
