from .BaseController import BaseController
from models.db_schemes import DataChunck, Project
from stores.LLM import LLMInterface, InputTypeEnum
from stores.vectordb import VectorDBInterface
from typing import List

class NLPController(BaseController):
    def __init__(self, vector_db_client: VectorDBInterface, 
                       embedding_client: LLMInterface, 
                       generation_client: LLMInterface):
        super().__init__()

        self.vector_db_client = vector_db_client
        self.embedding_client = embedding_client
        self.generation_client = generation_client


    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()
    

    def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id= project.project_id)
        return self.vector_db_client.delete_collection(collection_name= collection_name)
    

    def get_vector_db_collection_info(self, project: Project) -> dict:
        collection_name = self.create_collection_name(project_id= project.project_id)
        collection_info = self.vector_db_client.get_collection_info(collection_name= collection_name)

        return collection_info

    
    def index_vector_into_database(self, project: Project, chuncks: List[DataChunck],
                                         records_ids: List[str],
                                         do_reset: bool = False):
        
        if do_reset:
            self.reset_vector_db_collection(project= project)
        
        # Mangage Chuncks' Data
        metadata = [chunck.chunck_metadata for chunck in chuncks]
        texts = [chunck.chunck_text for chunck in chuncks]
        vectors = [
            self.embedding_client.embed_text(
                text=text, 
                document_type= InputTypeEnum.DOCUMENT.value
            ) 
            for text in texts
        ]

        # Create Collection if doesn't exist
        collection_name = self.create_collection_name(project_id= project.project_id)
        if not self.vector_db_client.is_collection_exist(collection_name= collection_name):
            self.vector_db_client.create_collection(
                collection_name= collection_name,
                embedding_size= self.embedding_client.embedding_size
            )

        # insert into database
        self.vector_db_client.insert_many(
            collection_name= collection_name,
            texts= texts,
            vectors= vectors,
            metadata= metadata,
            records_ids= records_ids
        )


        return True
        