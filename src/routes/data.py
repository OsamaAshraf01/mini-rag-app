from fastapi import APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from helpers import JSONResponses
from helpers.config import get_settings, Settings
from controllers import DataController, ProcessController, ProjectController
from models import ResponseEnum, DataChunk, ProjectModel, ChunkModel, AssetsModel
from .schemes.data import ProcessRequest
import aiofiles, logging, os
from models.db_schemes import Asset
from models.enums import AssetTypeEnum
from datetime import datetime

logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix='/api/v1/data',
    tags= ["api_v1", "data"]
)

@data_router.post("/upload/{project_id}")
async def upload_data(request: Request, project_id: str, file: UploadFile, app_settings: Settings = Depends(get_settings)):
    # To get app object, we used parameter of Request type
    # connect with database.
    project_model = await ProjectModel.create_instance(
        db= request.app.db
    )
    
    # Validate file
    data_controller = DataController()
    is_valid, msg = data_controller.validate_uploaded_file(file)

    if not is_valid:
        return JSONResponses.BAD_REQUEST(msg= msg)

    # Generate unique filename to avoid writing over exisitng files and to remove unwanted characters
    file_path, file_id = data_controller.generate_unique_filepath(
        original_name=file.filename, 
        project_id=project_id
    )

    # use try to avoid problems
    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNCK_SIZE):
                await f.write(chunk)
    except Exception as e:
        # use logger to avoid showing sensitive information to user. It will be in logger so the owner only
        # will be able to view and fix it
        logger.error(f"Error while uploading file: {e}")

        return JSONResponses.BAD_REQUEST(msg= ResponseEnum.FILE_UPLOAD_FAILED.value)
    
    assets_model = await AssetsModel.create_instance(
        db= request.app.db
    )

    file_extension = file_id.split('.')[-1]
    project = await project_model.get_project(project_id)
    asset = Asset(
        asset_project_id= project.id,
        asset_type= AssetTypeEnum.FILE.value,
        asset_extension= file_extension,
        asset_name= file_id,
        asset_size= os.path.getsize(file_path),
        asset_pushed_at= datetime.now()
    )

    asset.id = await assets_model.insert_asset(asset)

    return {
        "status" : ResponseEnum.FILE_UPLOAD_SUCCESS.value,
        "file_id" : str(asset.id)
    }
    


@data_router.post("/process/{project_id}")
async def process_endpoint(request:Request, project_id:str, process_request: ProcessRequest):
    process_controller = ProcessController(project_id=project_id)
    assets_model = await AssetsModel.create_instance(db= request.app.db)
    chunk_model = await ChunkModel.create_instance(db= request.app.db)
    project_model = await ProjectModel.create_instance(db= request.app.db)

    project = await project_model.get_project(project_id= project_id)

    request_file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    if request_file_id is not None:
        response = await assets_model.validate_file_id(request_file_id)
        if isinstance(response, JSONResponse):
            return response
        
        asset = await assets_model.get_asset(request_file_id)
        all_assets = [asset]
    else:
        # get files from all pages
        all_assets = await assets_model.get_all_project_assets(asset_project_id=project.id)
    
    if do_reset == 1:
        await chunk_model.delete_project_chunks(project_id= project.id)

    records_count = 0
    processed_files = 0
    for asset in all_assets:
        file_id = asset.asset_name
        file_content = process_controller.get_file_content(file_id=file_id)
        if file_content is None:
            logger.error(f"File not exist: file name \"{file_id}\".")
            continue

        chunks = process_controller.process_file_content(file_content, chunk_size=chunk_size, overlap_size=overlap_size) 
        if chunks is None or len(chunks) == 0:
            return JSONResponses.BAD_REQUEST(msg= ResponseEnum.PROCESSING_FAILED.value)



        # inserting chunk into database
        chunks = [
            DataChunk(
                chunk_text= chunk.page_content,
                chunk_metadata= chunk.metadata,
                chunk_order= i + 1,
                chunk_project_id= project.id,
                chunk_asset_id= asset.id
            )
            for i, chunk in enumerate(chunks)
        ]
        
        records_count += await chunk_model.insert_many_chunks(chunks)
        processed_files += 1

    total_chunks = await chunk_model.collection.count_documents({
        "chunk_project_id": project.id
    })
    return {
        "status": ResponseEnum.PROCESSING_SUCCESS.value,
        "processed_files": processed_files,
        # "result" : chunks,
        "inserted_chunks": records_count,
        "total_project_chunks": total_chunks
    }   