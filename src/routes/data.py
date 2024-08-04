from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController
from models import ResponseSignal
import aiofiles, logging # type: ignore
logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix='/api/v1/data'
)

@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)):
    
    data_controller = DataController()
    # Validate files
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

    # Use try to avoid problems
    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunck := await file.read(app_settings.FILE_DEFAULT_CHUNCK_SIZE):
                await f.write(chunck)
    except Exception as e:
        # using logger to avoid showing sensitive information to user. It will be in logger so the owner only
        # will be able to view and fix it
        logger.error(f"Error while uploading file: {e}")

        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content= {
                "status" : ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )

    return {
        "status" : ResponseSignal.FILE_UPLOAD_SUCCESS.value,
        "file_id" : file_id
    }
    
