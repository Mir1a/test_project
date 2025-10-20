from fastapi import FastAPI
from src.core.client.routers import router as client_router

app = FastAPI()

app.include_router(client_router)
