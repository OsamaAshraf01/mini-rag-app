from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.obectid import ObjectId #type: ignore

class DataChunck(BaseModel):
    _id: Optional[ObjectId] # _id sometimes may not be in the request or response 
    chunck_text: str = Field(..., min_length=1)
    chunck_metadata: dict
    chunck_order: int = Field(..., gt=0)  # order > 0
    chunck_project_id: ObjectId

    class Config:
        arbitary_types_allowed = True # To allow ObjectId type
