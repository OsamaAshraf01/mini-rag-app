from fastapi import UploadFile
from .BaseController import BaseController
from .ProjectController import ProjectController
from models import ResponseSignal
import os, re

class DataController(BaseController):
    def __init__(self):
        super().__init__()


    def validate_uploaded_file(self, file: UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value
        
        if file.size > self.app_settings.FILE_MAX_SIZE * 1024 * 1024:
            return False, ResponseSignal.FILE_SIZE_EXEEDED.value
        
        return True, ResponseSignal.FILE_UPLOAD_SUCCESS.value
    

    def get_clean_filename(self, original_name:str):
        cleaned_file_name = re.sub(r'[^\w.]', '', original_name.strip())
        cleaned_file_name = cleaned_file_name.replace(" ", "_")

        return cleaned_file_name


    def generate_unique_filepath(self, original_name:str, project_id:str):
        random_key = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)

        cleaned_filename =  self.get_clean_filename(original_name)

        new_file_path = os.path.join(project_path, random_key + "_" + cleaned_filename)

        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(project_path, random_key + "_" + cleaned_filename)

        return new_file_path, random_key + "_" + cleaned_filename
