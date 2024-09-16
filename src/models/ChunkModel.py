from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from .db_schemes import DataChunk
from bson.objectid import ObjectId
from pymongo import InsertOne
from typing import List
from helpers.custom_assertions import AssertExistence
from helpers import execution_manager

class ChunkModel(BaseDataModel):
    indexes = DataChunk.get_indexes()

    def __init__(self, db):
        self.collection_name = DataBaseEnum.CHUNCK_COLLECTION_NAME.value
        super().__init__(db=db)


    async def insert_chunk(self, chunk:DataChunk) -> ObjectId:
        ''' This function is to insert a new chunk into the database
            and returning an object of type ObjectId.
            This function should be called only if chunk is not found in the database.
        '''

        result = await self.collection.insert_one(chunk.model_dump(by_alias=True, exclude_unset=True)) # = chunk.dict()
        return result.inserted_id
    

    async def insert_many_chunks(self, chunks:List[DataChunk], batch_size:int = 100) -> int:
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            operations = [InsertOne(chunk.model_dump(by_alias=True, exclude_unset=True)) for chunk in batch]
            
            await self.collection.bulk_write(operations)
        
        # We used bulk write to make inserting more effecient than repeated insert_one
        return len(chunks)
    
    @execution_manager
    async def get_chunk(self, chunk_id:str) -> DataChunk:
        record = await self.collection.find_one({
            "_id": ObjectId(chunk_id)
        })

        AssertExistence(record)
            
        return DataChunk(**record)


    @execution_manager
    async def get_project_chunks(self, project_id:ObjectId, page:int = 1, page_size:int = 50) -> List[DataChunk]:
        skipped = (page - 1) * page_size
        
        result = self.collection.find({
                "chunk_project_id": project_id
        }).skip(skipped).limit(page_size)
        
        AssertExistence(result)
        
        chunks = []
        async for record in result:
            chunks.append(DataChunk(**record))

        return chunks


    async def get_all_chunks(self, page:int = 1, page_size:int = 10) -> List[DataChunk]:
        total_records = await self.collection.count_documents({})
        total_pages = total_records // page_size + int(total_records % page_size != 0)
        skipped_count = (page - 1) * page_size

        cursor = self.collection.find().skip(skipped_count).limit(page_size)

        chunks = []
        async for document in cursor:
            chunks.append(
                DataChunk(**document)
            )

        return chunks, total_pages
    

    async def delete_project_chunks(self, project_id: ObjectId):
        result = await self.collection.delete_many({
            "chunk_project_id": project_id
        })

        return result.deleted_count