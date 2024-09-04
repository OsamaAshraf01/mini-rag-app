from helpers.config import get_settings

class BaseDataModel:
    def __init__(self, db):
        self.db = db
        self.settings = get_settings()