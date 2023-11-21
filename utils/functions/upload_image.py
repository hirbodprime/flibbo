from .get_filename_ext import get_filename_ext



class ImageUploadHandler:
    def __init__(self, folder_name, prefix, type_):
        self.folder_name = folder_name
        self.prefix = prefix
        self.type = type_

    def get_filename(self, instance, filename):
        name, ext = get_filename_ext(filename)
        final_name = f"{self.prefix}-{instance.user}-{ext}"
        return f"users/{instance.user}/data/{self.type}/{self.folder_name}/{final_name}"






