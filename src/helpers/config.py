from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi import FastAPI
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    OPENAI_KEY: str
    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNCK_SIZE: int

    MONGODB_URL: str
    MONGODB_DATABASE: str

    class Config:
        env_file = '.env'


def get_settings():
    return Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.client = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db = app.client[settings.MONGODB_DATABASE]

    yield  # Logic before yield is executed before start and Logic after it will be executed after finish.
           # That is because of @asynccontextmanager (async context manager)

    app.client.close()