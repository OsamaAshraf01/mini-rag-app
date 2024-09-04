from fastapi import APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProcessController
from models import ResponseEnum, ProjectModel
from .schemes.data import ProcessRequest
import aiofiles, logging # type: ignore

logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix='/api/v1/data'
)

@data_router.post("/upload/{project_id}")
async def upload_data(request: Request, project_id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)):
    # To get app object, we used parameter of Request type
    # connect with database.
    project_model = ProjectModel(
        db= request.app.db
    )
    project = await project_model.get_project(project_id= project_id)
    
    
    data_controller = DataController()

    # Validate file
    is_valid, msg = data_controller.validate_uploaded_file(file)

    if not is_valid:
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content = {
                "upload_status" : is_valid,
                "Error" : msg
            }
        )

    # Generate unique filename to avoid writing over exisitng files and to remove unwanted characters
    file_path, file_id = data_controller.generate_unique_filepath(
        original_name=file.filename, 
        project_id=project_id
    )

    # use try to avoid problems
    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunck := await file.read(app_settings.FILE_DEFAULT_CHUNCK_SIZE):
                await f.write(chunck)
    except Exception as e:
        # use logger to avoid showing sensitive information to user. It will be in logger so the owner only
        # will be able to view and fix it
        logger.error(f"Error while uploading file: {e}")

        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content= {
                "status" : ResponseEnum.FILE_UPLOAD_FAILED.value
            }
        )

    return {
        "status" : ResponseEnum.FILE_UPLOAD_SUCCESS.value,
        "file_id" : file_id
    }
    


@data_router.post("/process/{project_id}")
async def process_endpoint(project_id:str, process_request: ProcessRequest):
    file_id = process_request.file_id
    process_controller = ProcessController(project_id=project_id)

    file_content = process_controller.get_file_content(file_id=file_id)
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset


    chunks = process_controller.process_file_content(file_content, chunk_size=chunk_size, overlap_size=overlap_size) 
    
    if chunks is None or len(chunks) == 0:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content= {
                "status" : ResponseEnum.PROCESSING_FAILED.value
            }
        )

    return {
        "status" : ResponseEnum.PROCESSING_SUCCESS.value,
        "result" : chunks
    }   