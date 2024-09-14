from .VectorDBEnums import VectorDBEnums
from .providers import QdrantDBProvider
from helpers.config import Settings
from controllers import BaseController

class VectorDBProviderFactory:
    def __init__(self, config: Settings):
        self.config = config
        self.base_controller = BaseController()

    def create(self, db_provider_name: str):
        if db_provider_name == VectorDBEnums.QDRANT.value:
            db_folder = self.config.VECTOR_DB_FOLDER
            db_path = self.base_controller.get_database_path(db_folder)

            return QdrantDBProvider(
                db_path= db_path,
                distance_method= self.config.VECTOR_DB_DISTANCE_METHOD
            )
        
        return None