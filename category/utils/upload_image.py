from utils.functions.get_filename_ext import get_filename_ext

class ImageUploadHandler:
    def __init__(self, folder_name, prefix):
        self.folder_name = folder_name
        self.prefix = prefix

    def __call__(self, instance, filename):
        name, ext = get_filename_ext(filename)
        final_name = f"{self.prefix}-{instance.name}-{ext}"
        try:
            return f"categories/{self.folder_name}/{instance.parent}/{instance.name}/{final_name}"
        except:
            return f"categories/{self.folder_name}/{instance.name}/{final_name}"
