from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId 

class DataChunck(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id") # _id sometimes may not be in the request or response 
    chunck_text: str = Field(..., min_length=1)
    chunck_metadata: dict
    chunck_order: int = Field(..., gt=0)  # order > 0
    chunck_project_id: ObjectId
    chunck_asset_id: ObjectId

    class Config:
        arbitrary_types_allowed = True # To allow ObjectId type


    @classmethod
    def get_indexes(cls):
        return[
            {
                "keys": [
                    ("chunck_project_id", 1) # 1 for ascending, -1 for descending
                    # Add more keys here if will be used in the same condition
                ],
                "name": "chunck_project_id_index_1",
                "unique": False
            },
            # Add more keys here if will be used in separate conditions
        ]
