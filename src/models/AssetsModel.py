from models import BaseDataModel
from .enums import DataBaseEnum
from .db_schemes import Asset
from bson.objectid import ObjectId
from typing import List


class AssetsModel(BaseDataModel):
    indexes = Asset.get_indexes()

    def __init__(self, db):
        self.collection_name = DataBaseEnum.ASSETS_COLLECTION_NAME.value
        super().__init__(db)

    
    async def insert_asset(self, asset:Asset) -> ObjectId:
        result = await self.collection.insert_one(asset.model_dump(by_alias=True, exclude_unset=True))
        return result.inserted_id
    

    async def get_asset(self, asset_id:str) -> Asset:
        document = await self.collection.find_one({
            "_id": ObjectId(asset_id)
        })

        if document is None:
            return None

        return Asset(**document)


    async def get_assets_by_project_id(self, project_id:str, page:int=1, page_size:int=10) -> List[Asset]:
        total_records = await self.collection.count_documents({
            "asset_project_id": ObjectId(project_id)
        })

        total_pages = total_records // page_size + int(total_records % page_size != 0)
        skipped_count = (page - 1) * page_size

        cursor = self.collection.find({
            "asset_project_id": ObjectId(project_id)
        }).skip(skipped_count).limit(page_size)

        assets = []

        async for document in cursor:
            assets.append(Asset(**document))

        return assets, total_pages
        