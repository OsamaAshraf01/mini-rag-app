from helpers.config import get_settings

class BaseDataModel:
    def __init__(self, db):
        self.db = db
        self.settings = get_settings()


    async def init_collection(self, indexes):
        all_collections = await self.db.list_collection_names()
        target_collection_name = self.collection_name

        if target_collection_name not in all_collections:
            self.collection = self.db[self.collection_name]

            for index in indexes:
                await self.collection.create_index(**index)
                # await self.collection.create_index(
                #     index["key"],
                #     name= index["name"],
                #     unique= index["unique"]
                # )