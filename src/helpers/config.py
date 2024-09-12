from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi import FastAPI
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNCK_SIZE: int

    MONGODB_URL: str
    MONGODB_DATABASE: str

    OPENAI_API_KEY: str = None
    COHERE_API_KEY: str = None

    GENERATION_BACKEND: str
    GENERATION_MODEL_ID: str = None
    OPENAI_API_URL: str = None

    EMBEDDING_BACKEND: str
    EMBEDDING_MODEL_ID: str = None
    EMBEDDING_SIZE: int = None

    DEFAULT_INPUT_MAX_CHARACTERS: int = None
    DEFAULT_GENERATION_MAX_OUTPUT_TOKENS: int = None
    DEFAULT_GENERATION_TEMPRATURE: float = None

    VECTOR_DB_BACKEND: str
    VECTOR_DB_FOLDER: str
    VECTOR_DB_DISTANCE_METHOD: str
    class Config:
        env_file = '.env'


def get_settings():
    return Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from stores.LLM.LLMProviderFactory import LLMProviderFactory
    
    settings = get_settings()
    app.client = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db = app.client[settings.MONGODB_DATABASE]

    llm_provider_factory = LLMProviderFactory(settings)

    # Generation Client
    app.generation_client = llm_provider_factory.create(settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id= settings.GENERATION_MODEL_ID)

    # Embedding Client
    app.embedding_client = llm_provider_factory.create(settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id= settings.EMBEDDING_MODEL_ID, embedding_size= settings.EMBEDDING_SIZE)

    yield  # Logic before yield is executed before start and Logic after it will be executed after finish.
           # That is because of @asynccontextmanager (async context manager)

    app.client.close()