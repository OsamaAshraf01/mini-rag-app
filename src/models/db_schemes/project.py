from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.obectid import ObjectId #type: ignore

class Project(BaseModel):
    _id: Optional[ObjectId] # _id sometimes may not be in the request or response
    project_id: str = Field(..., min_length=1) # To validate length

    @field_validator('project_id')
    def validate_project_id(cls, id: str):
        if not id.isalnum():
            raise ValueError("Project ID must be alphanumeric")
        
        return id


    class Config:
        arbitary_types_allowed = True # To allow ObjectId type
