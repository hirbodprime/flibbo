from utils.functions.get_filename_ext import get_filename_ext
from utils.functions.upload_image import ImageUploadHandler
import uuid


class PostUploadHandler(ImageUploadHandler):
    def get_filename(self, instance, filename):
        name, ext = get_filename_ext(filename)
        unique_name = str(uuid.uuid4())
        final_name = f"{self.prefix}-{instance.slug}-{ext}"
        return f"users/{instance.user}/data/{self.type}/{self.folder_name}/{instance.slug}/{final_name}"


class ProfileUploadHandler(ImageUploadHandler):
    def get_filename(self, instance, filename):
        name, ext = get_filename_ext(filename)
        unique_name = str(uuid.uuid4())
        final_name = f"{self.prefix}-{instance.username}-{ext}"
        return f"users/{instance.email}/data/{self.type}/{self.folder_name}/{instance.username}/{final_name}"
