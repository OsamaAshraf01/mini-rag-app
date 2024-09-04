from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from .db_schemes import Project
from typing import List

class ProjectModel(BaseDataModel):
    def __init__(self, db):
        super().__init__(db=db)
        self.collection = self.db[DataBaseEnum.PROJECT_COLLECTION_NAME.value]


    async def insert_project(self, project:Project) -> Project:
        # inserting a new record
        result = await self.collection.insert_one(project.model_dump()) # Converting pytdantic model into dictionary
        
        # assigning new id
        project._id = result.inserted_id

        return project
    

    async def get_project(self, project_id:str) -> Project:
        """
        get project from the database. If not found a new one will be created and returned
        """
        record = await self.collection.find_one({
            "project_id" : project_id
        })

        if record is None:
            project = Project(project_id=project_id)
            project = await self.insert_project(project=project)

            return project
        
        return Project(**record) # record is a dict so we unpacked it and wrapped it in a Project object
    

    async def get_all_projects(self, page:int=1, page_size:int=10) -> List[Project]:
        total_records = self.collection.count_documents({}) # {} means count all
        total_pages = total_records // page_size + int(total_records % page != 0)
        skipped_count = (page - 1) * page_size
        
        cursor = self.collection.find().skip(skipped_count).limit(page_size)

        projects = []
        async for document in cursor: # more effecient way than list(cursor)
            projects.append(
                Project(**document)
            )

        return projects, total_pages



