from fastapi import FastAPI, APIRouter, Depends
from helpers.config import get_settings, Settings

base_router = APIRouter(
    prefix='/api/v1'
)

@base_router.get('/')
async def welcome(app_settings:Settings = Depends(get_settings)):  # Make the variable as a Depend to ensure that it is available before starting function's work
    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION
    return {
        "app_name" : app_name,
        "app_verion" : app_version,   
    }