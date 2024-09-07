from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from .db_schemes import DataChunck
from bson.objectid import ObjectId
from pymongo import InsertOne
from typing import List

class ChunckModel(BaseDataModel):
    def __init__(self, db):
        super().__init__(db=db)
        self.collection_name = DataBaseEnum.CHUNCK_COLLECTION_NAME.value
        all_collections = self.db.list_collection_names()

        if self.collection_name in all_collections:
            self.collection = self.db[self.collection_name]


    @classmethod
    async def create_instance(cls, db):
        instance = cls(db)
        await instance.init_collection(DataChunck.get_indexes())
        return instance


    async def insert_chunck(self, chunck:DataChunck) -> ObjectId:
        ''' This function is to insert a new chunck into the database
            and returning an object of type ObjectId.
            This function should be called only if chunck is not found in the database.
        '''

        result = await self.collection.insert_one(chunck.model_dump(by_alias=True, exclude_unset=True)) # = chunck.dict()
        return result.inserted_id
    

    async def get_chunck(self, chunck_id:str) -> DataChunck:
        record = await self.collection.find_one({
            "_id": ObjectId(chunck_id)
        })

        if record is None:
            return None
            
        return DataChunck(**record)


    async def get_all_chuncks(self, page:int = 1, page_size:int = 10):
        total_records = self.collection.count_documents({})
        total_pages = total_records // page_size + int(total_records % page_size != 0)
        skipped_count = (page - 1) * page_size

        cursor = self.collection.find().skip(skipped_count).limit(page_size)

        chuncks = []
        async for document in cursor:
            chuncks.append(
                DataChunck(**document)
            )

        return chuncks, total_pages
    

    async def insert_many_chuncks(self, chuncks:List[DataChunck], batch_size:int = 100):
        for i in range(0, len(chuncks), batch_size):
            batch = chuncks[i:i+batch_size]
            operations = [InsertOne(chunck.model_dump(by_alias=True, exclude_unset=True)) for chunck in batch]
            
            await self.collection.bulk_write(operations)
        
        # We used bulk write to make inserting more effecient than repeated insert_one
        return len(chuncks)
    

    async def delete_chuncks_by_project_id(self, project_id: ObjectId):
        result = await self.collection.delete_many({
            "chunck_project_id": project_id
        })

        return result.deleted_count