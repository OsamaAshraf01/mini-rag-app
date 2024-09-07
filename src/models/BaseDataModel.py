from helpers.config import get_settings

class BaseDataModel:
    def __init__(self, db):
        self.db = db
        self.settings = get_settings()

        self.collection = self.db[self.collection_name] 
        # This line doesn't create a new collection in the database, it only prepares the reference to the collection
        # The new collection is actually created in the database with the first insert.


    @classmethod
    async def create_instance(cls, db):
        instance = cls(db)
        await instance.init_collection(cls.indexes)
        return instance


    async def init_collection(self, indexes):
        all_collections = await self.db.list_collection_names()

        if self.collection_name not in all_collections:
            for index in indexes:
                await self.collection.create_index(**index)
