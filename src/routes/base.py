from fastapi import FastAPI, APIRouter, Depends
from helpers.config import get_settings, Settings

base_router = APIRouter(
    prefix='/api/v1'
)

# Depends function is very impoortant. It makes your application more efficient
# It means that: Don't start in the logic of the function until you get a ressponse from
# a specific another function.
@base_router.get('/')
async def welcome(app_settings:Settings = Depends(get_settings)):  # Make the variable as a Depend to ensure that it is available before starting function's work
    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION
    allowed_files = app_settings.FILE_ALLOWED_TYPES
    max_size = app_settings.FILE_MAX_SIZE

    return {
        "app_name" : app_name,
        "app_verion" : "v" + app_version,
        "allowed_types" : allowed_files,
        "max_size" : str(max_size) + "Mb"
    }