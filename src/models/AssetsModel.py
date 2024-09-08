from models import BaseDataModel
from .enums import DataBaseEnum
from .db_schemes import Asset
from bson.objectid import ObjectId
from typing import List
from fastapi.responses import JSONResponse
from fastapi import status
from .enums import ResponseEnum, AssetTypeEnum


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


    async def get_assets_by_project_id(self, asset_project_id:ObjectId, asset_types:List[str], page:int=1, page_size:int=10) -> List[Asset]:
        total_records = await self.collection.count_documents({
            "asset_project_id": asset_project_id,
            "$or": [
                {"asset_type" : type} for type in asset_types
            ]
        })

        total_pages = total_records // page_size + int(total_records % page_size != 0)
        skipped_count = (page - 1) * page_size

        cursor = self.collection.find({
            "asset_project_id": asset_project_id
        }).skip(skipped_count).limit(page_size)

        assets = []

        async for document in cursor:
            assets.append(Asset(**document))

        return assets, total_pages
    

    async def get_all_project_assets(self, asset_project_id:ObjectId) -> List[Asset]:
        total_records = await self.collection.count_documents({
            "asset_project_id": asset_project_id
        }) 

        assets, _ = await self.get_assets_by_project_id(
            asset_project_id=asset_project_id, 
            asset_types=[AssetTypeEnum.FILE.value],
            page=1, 
            page_size=total_records
        )

        return assets


    async def validate_file_id(self, asset_id):
        if not ObjectId.is_valid(asset_id):
            return JSONResponse(
                status_code= status.HTTP_400_BAD_REQUEST,
                content= {
                    "status" : ResponseEnum.INVALID_ID.value
                }
            )
        asset = await self.get_asset(asset_id)

        if asset is None:
            return JSONResponse(
                status_code= status.HTTP_400_BAD_REQUEST,
                content= {
                    "status" : ResponseEnum.FILE_NOT_FOUND.value
                }
            )
