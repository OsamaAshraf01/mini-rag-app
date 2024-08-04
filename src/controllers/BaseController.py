from helpers.config import get_settings
from helpers.config import Settings
import os, random, string

class BaseController:
    def __init__(self):
        self.app_settings = get_settings()
        self.base_dir = os.path.dirname( os.path.dirname(__file__) )  # To get the dir of src folder
        self.files_dir = os.path.join(self.base_dir, "assets/files")


    def generate_random_string(self, length:int = 12):
        return ''.join(random.choices(string.ascii_lowercase + string.digits,k=length))
