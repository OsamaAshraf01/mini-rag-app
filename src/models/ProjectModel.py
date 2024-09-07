from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from .db_schemes import Project
from typing import List
from bson.objectid import ObjectId

class ProjectModel(BaseDataModel):
    indexes = Project.get_indexes()

    def __init__(self, db):
        self.collection_name = DataBaseEnum.PROJECT_COLLECTION_NAME.value
        super().__init__(db=db)


    async def insert_project(self, project:Project) -> ObjectId:
        # inserting a new record
        result = await self.collection.insert_one(project.model_dump(by_alias=True, exclude_unset=True)) # Converting pytdantic model into dictionary    # by_alias to use aliases if found    # exclude_unset to exclude parameters is have a default value of None
        return result.inserted_id
    

    async def get_project(self, project_id:str) -> Project:
        """
        get project from the database. If not found a new one will be created and returned
        """
        record = await self.collection.find_one({
            "project_id" : project_id
        })

        if record is None:
            project = Project(project_id=project_id)
            project.id = await self.insert_project(project=project)

            return project
        
        return Project(**record) # record is a dict so we unpacked it and wrapped it in a Project object
    

    async def get_all_projects(self, page:int=1, page_size:int=10) -> List[Project]:
        total_records = await self.collection.count_documents({}) # {} means count all
        total_pages = total_records // page_size + int(total_records % page != 0)
        skipped_count = (page - 1) * page_size
        
        cursor = self.collection.find().skip(skipped_count).limit(page_size)

        projects = []
        async for document in cursor: # more effecient way than list(cursor)
            projects.append(
                Project(**document)
            )

        return projects, total_pages



