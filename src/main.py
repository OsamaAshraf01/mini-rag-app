from fastapi import FastAPI
from routes import base, data
from helpers.config import lifespan

app = FastAPI(lifespan=lifespan)
app.include_router(base.base_router)
app.include_router(data.data_router)
