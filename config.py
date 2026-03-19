# config.py -- load .env valuse
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/jobportal")

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587 # Standard Gmail SMTP port
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    # ADD THIS LINE
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_USERNAME")

    # -----------------------------
    # Uploads
    # -----------------------------
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
    UPLOAD_FOLDER_PROFILS = os.getenv("UPLOAD_FOLDER_PROFILS" , "static/profile_img")

    # -----------------------------
    # Job matching
    # -----------------------------
    JOB_POSTS_COLLECTION = os.getenv("JOB_POSTS_COLLECTION", "job_posts")

    RESUME_DATASET_PATH = os.getenv("RESUME_DATASET_PATH", os.path.join("data", "Resume.csv"))
