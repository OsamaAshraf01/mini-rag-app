from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import uuid
from helpers import JSONResponses
from .schemes.nlp import PushRequest
from models import ProjectModel, ChunckModel
from models.enums import ResponseEnum
from controllers import NLPController
from datetime import datetime
import logging

logger = logging.getLogger("uvicorn.error")

nlp_router = APIRouter(
    prefix= "/api/v1/nlp",
    tags= ["api_v1", "nlp"]
)

@nlp_router.post("/index/push/{project_id}")
async def push(request: Request, project_id: str, push_request: PushRequest):
    project_model = await ProjectModel.create_instance(db= request.app.db)
    chunck_model = await ChunckModel.create_instance(db= request.app.db)
    nlp_controller = NLPController(
        vector_db_client= request.app.vector_db_client,
        embedding_client= request.app.embedding_client,
        generation_client= request.app.generation_client
    )

    project = await project_model.get_project(project_id= project_id)
    do_reset = push_request.do_reset

    if project is None:
        return JSONResponses.BAD_REQUEST(msg= ResponseEnum.PROJECT_NOT_FOUND.value)
    
    # get all project chuncks
    chuncks = []
    page_no = 1
    while True:
        page_chuncks = await chunck_model.get_project_chuncks(project_id= project.id, page= page_no)
        if page_chuncks is None or len(page_chuncks) == 0:
            break
        chuncks += page_chuncks
        page_no += 1

    records_ids = [
        str(uuid.uuid4())
        for i in range(len(chuncks))
    ]

    nlp_controller.index_vector_into_database(
        project= project, 
        chuncks= chuncks, 
        do_reset= do_reset,
        records_ids= records_ids
    )
    

    return JSONResponses.OK(
        content={
            "signal": ResponseEnum.INSERT_INTO_VECTORDB_SUCCESS.value,
            "inserted_items_count": len(chuncks)
        }
    )


@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: str):
    project_model = await ProjectModel.create_instance(db= request.app.db)
    nlp_controller = NLPController(
        vector_db_client= request.app.vector_db_client,
        embedding_client= request.app.embedding_client,
        generation_client= request.app.generation_client
    )

    project = await project_model.get_project(project_id= project_id)

    return JSONResponse(
        content={
            "signal": ResponseEnum.VECTORDB_COLLECTION_RETRIEVED.value,
            "project_collection_info": nlp_controller.get_vector_db_collection_info(project)
        }
    )
