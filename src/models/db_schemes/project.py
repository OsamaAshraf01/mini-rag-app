from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId 

class Project(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id") # _id sometimes may not be in the request or response
    project_id: str = Field(..., min_length=1) # To validate length
    # NOTE: _id is the id in database, while project_id is the id that we use to upload/process files


    @field_validator('project_id')
    def validate_project_id(cls, id: str):
        if not id.isalnum():
            raise ValueError("Project ID must be alphanumeric")
        
        return id


    class Config:
        arbitrary_types_allowed = True # To allow ObjectId type
