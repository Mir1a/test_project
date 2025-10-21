from fastapi import FastAPI
from src.core.client.routers import router as client_router
from src.core.auth.routers import router as auth_router
from src.core.crm.routers import router as crm_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(client_router)
app.include_router(crm_router)