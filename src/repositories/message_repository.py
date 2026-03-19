from src.database.mongo import db

class MessageRepository:
    def __init__(self):
        self.col = db["messages"]

    def save_message(self, message_data):
        return self.col.insert_one(message_data)
    
    def get_all_messages(self):
        return list(self.col.find().sort("submitted_at", -1))
    

    def delete_message(self, msg_id):
        from bson import ObjectId

        try:
            result = self.col.delete_one({"_id": ObjectId(msg_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting message: {e}")
            return False