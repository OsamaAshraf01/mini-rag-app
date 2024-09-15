from qdrant_client import QdrantClient, models
from qdrant_client.conversions.common_types import ScoredPoint
from qdrant_client.models import VectorParams
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
from typing import List
import logging

class QdrantDBProvider(VectorDBInterface):
    def __init__(self, db_path: str, distance_method: str):
        self.db_path = db_path
        self.distance_method = None
        self.client = None

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT

        self.logger = logging.getLogger(__name__)


    def connect(self):
        self.client = QdrantClient(path=self.db_path)


    def disconnect(self):
        self.client = None


    def list_all_collections(self) -> List:
        return self.client.get_collections()


    def is_collection_exist(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name= collection_name)


    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name= collection_name).model_dump()

    
    def delete_collection(self, collection_name: str):
        if self.is_collection_exist(collection_name=collection_name):
            return self.client.delete_collection(collection_name=collection_name)

    
    def create_collection(self, collection_name: str, 
                                embedding_size: int, 
                                do_reset: bool = False):
        
        if do_reset:
            self.delete_collection(collection_name= collection_name)

        if self.is_collection_exist(collection_name= collection_name):
            self.logger.error(f"Collection '{collection_name}' already exists in database.")
            return False
                
        self.client.create_collection(
            collection_name= collection_name,
            vectors_config= VectorParams(
                size= embedding_size, 
                distance= self.distance_method
            )
        )


    def insert_one(self, collection_name: str, text: str, vector: list,
                         record_id: str,
                         metadata: dict = None) -> bool:
        if not self.is_collection_exist(collection_name= collection_name):
            self.logger.error(f"Collection '{collection_name} doesn't exist in database.'")
            return False
        
        try:
            self.client.upload_records(
                collection_name= collection_name,
                records=[
                    models.Record(
                        id= record_id,
                        vector= vector,
                        payload= {
                            "text": text,
                            "metadata": metadata
                        }
                    )
                ]
            )
        except Exception as e:
            self.logger.error(f"Error while inserting record into collection {collection_name}: {e}")
            return False

        return True


    def insert_many(self, collection_name: str, texts: List[str], vectors: List[list],
                         records_ids: List[str],
                         metadata: List[dict] = None, batch_size: int = 50):
        if not self.is_collection_exist(collection_name= collection_name):
            self.logger.error(f"Collection '{collection_name} doesn't exist in database.'")
            return False
        
        for batch in range(0, len(vectors), batch_size):
            try:
                self.client.upload_records(
                    collection_name= collection_name,
                    records=[
                        models.Record(
                            id= records_ids[i],
                            vector= vectors[i],
                            payload= {
                                "text": texts[i],
                                "metadata": metadata[i] if metadata else None
                            }
                        )
                        for i in range(batch, min(batch + batch_size, len(vectors)))
                    ]
                )
            
            except Exception as e:
                self.logger.error(f"Error while inserting records into collection {collection_name}: {e}")
                return False

        return True


    def search_by_vector(self, collection_name: str, vector: list, limit: int = 5) -> List[ScoredPoint]:
        search_results = self.client.search(
            collection_name= collection_name,
            query_vector= vector,
            limit= limit
        )

        return search_results
         