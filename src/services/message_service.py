from src.repositories.message_repository import MessageRepository
from datetime import datetime

class MessageService:
    def __init__(self):
        self.message_repo = MessageRepository()

    def submit_contact_message(self, name, email, subject, message):
        
        if not name or not email or not message:
            return False, "Name, Email, and Message are required fields."

        message_document = {
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
            "status": "unread", 
            "submitted_at": datetime.utcnow()
        }

        try:
            self.message_repo.save_message(message_document)
            return True, "Your message has been sent successfully! We will get back to you soon."
        except Exception as e:
            return False, "An error occurred while sending your message. Please try again later."
        
    def get_all_messages(self):
        return self.message_repo.get_all_messages()
    
    def get_unread_count(self):
        return self.message_repo.col.count_documents({"status": "unread"})

    def mark_all_as_read(self):
        self.message_repo.col.update_many({"status": "unread"}, {"$set": {"status": "read"}})