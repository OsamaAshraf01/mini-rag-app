from fastapi import APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from helpers.config import get_settings, Settings
from controllers import DataController, ProcessController, ProjectController
from models import ResponseEnum, DataChunck, ProjectModel, ChunckModel, AssetsModel
from .schemes.data import ProcessRequest
import aiofiles, logging, os
from models.db_schemes import Asset
from models.enums import AssetTypeEnum
from datetime import datetime

logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix='/api/v1/data'
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
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content = {
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
    
    assets_model = await AssetsModel.create_instance(
        db= request.app.db
    )

    file_extension = file_id.split('.')[-1]
    project = await project_model.get_project(project_id)
    asset = Asset(
        asset_project_id= project.id,
        asset_type= AssetTypeEnum.FILE.value + '/' + file_extension,
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
    chunck_model = await ChunckModel.create_instance(db= request.app.db)
    project_model = await ProjectModel.create_instance(db= request.app.db)

    project = await project_model.get_project(project_id= project_id)

    request_file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    if do_reset == 1:
        await chunck_model.delete_chuncks_by_project_id(project.id)

    if request_file_id is not None:
        response = await assets_model.validate_file_id(request_file_id)
        if isinstance(response, JSONResponse):
            return response
        
        asset = await assets_model.get_asset(request_file_id)
        files_names = [asset.asset_name]
    else:
        # get files from all pages
        all_files = await assets_model.get_all_project_assets(asset_project_id=project.id)
        files_names = [asset.asset_name for asset in all_files]
    
    records_count = 0
    for file_id in files_names:
        file_content = process_controller.get_file_content(file_id=file_id)
        chuncks = process_controller.process_file_content(file_content, chunk_size=chunk_size, overlap_size=overlap_size) 
        
        if chuncks is None or len(chuncks) == 0:
            return JSONResponse(
                status_code= status.HTTP_400_BAD_REQUEST,
                content= {
                    "status" : ResponseEnum.PROCESSING_FAILED.value
                }
            )



        # inserting chunck into database
        chuncks = [
            DataChunck(
                chunck_text= chunck.page_content,
                chunck_metadata= chunck.metadata,
                chunck_order= i + 1,
                chunck_project_id= project.id
            )
            for i, chunck in enumerate(chuncks)
        ]
        
        records_count += await chunck_model.insert_many_chuncks(chuncks)

    total_chuncks = await chunck_model.collection.count_documents({
        "chunck_project_id": project.id
    })
    return {
        "status" : ResponseEnum.PROCESSING_SUCCESS.value,
        # "result" : chuncks,
        "inserted_chuncks": records_count,
        "total_chuncks": total_chuncks
    }   