from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from .db_schemes import DataChunck
from bson.objectid import ObjectId
from pymongo import InsertOne

class ChunckModel(BaseDataModel):
    def __init__(self, db):
        super().__init__(db=db)
        self.collection = self.db[DataBaseEnum.CHUNCK_COLLECTION_NAME.value]


    async def insert_chunck(self, chunck:DataChunck) -> DataChunck:
        ''' This function is to insert a new chunck into the database
            and returning an object of type DataChunck contining _id attribute.
            This function should be called only if chunck is not found in the database.
        '''

        result = await self.collection.insert_one(chunck.model_dump()) # = chunck.dict()
        chunck._id = result.inserted_id

        return chunck
    

    async def get_chunck(self, chunck_id:str) -> DataChunck | None:
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
    

    async def insert_many_chuncks(self, chuncks:list, batch_size:int = 100):
        for i in range(0, len(chuncks), batch_size):
            batch = chuncks[i:i+batch_size]
            operations = [InsertOne(chunck.model_dump()) for chunck in batch]
            
            await self.collection.bulk_write(operations)
        
        # We used bilk write to make inserting more effecient than repeated insert_one
        return len(chuncks)