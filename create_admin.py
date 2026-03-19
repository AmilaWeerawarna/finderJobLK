# create_admin.py

import os

from src.repositories.user_repository import UserRepository
from werkzeug.security import generate_password_hash

password = os.getenv("ADMIN_PASSWORD") # Better way to Security Improvements 

repo = UserRepository()
email = "admin@example.com"
name = "Admin"
hashed = generate_password_hash(password)
created = repo.create_admin_if_not_exists(email, name, hashed)
if created:
    print("Admin created:", email)
else:
    print("Admin already exists.")
    
