from src.repositories.user_repository import UserRepository
from src.utils.image_helper import compress_and_save_image

class ProfileService:
    def __init__(self):
        self.user_repo = UserRepository()

    def get_employer_profile(self, user_id):
        return self.user_repo.find_by_id(user_id)

    def update_employer_profile(self, email, update_data, image_file=None, upload_folder=None):
        updated_image_name = None
        
        if image_file and upload_folder:
            updated_image_name = compress_and_save_image(image_file, upload_folder, prefix="emp")
            if updated_image_name:
                update_data["profile_image"] = updated_image_name

        self.user_repo.update_user(email, update_data)
        return updated_image_name