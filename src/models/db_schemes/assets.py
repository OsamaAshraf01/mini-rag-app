from pydantic import BaseModel, Field
from typing import Optional
from bson.objectid import ObjectId

class Asset(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    asset_project_id: ObjectId
    asset_type: str
    asset_name: str


    class Config:
        arbitrary_types_allowed = True
