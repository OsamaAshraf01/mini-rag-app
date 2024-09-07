from pydantic import BaseModel, Field
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime

class Asset(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    asset_project_id: ObjectId
    asset_type: str = Field(..., min_length=1) # ... means required field
    asset_name: str = Field(..., min_length=1)
    asset_size: int = Field(default=None, ge=0)
    asset_pushed_at: datetime = Field(default=datetime.now())


    class Config:
        arbitrary_types_allowed = True


    @classmethod
    def get_indexes(cls):
        return [
            {
                "keys": [
                    ("asset_project_id", 1)
                ],
                "name":"asset_project_id_index_1",
                "unique": False
            },
            {
                "keys": [
                    ("asset_project_id", 1),
                    ("asset_name", 1),
                ],
                "name":"asset_name_project_id_index_1",
                "unique": True
            },
        ]