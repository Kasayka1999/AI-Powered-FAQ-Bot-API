from fastapi import APIRouter

from app.api.v1.routers import login, registration

master_router = APIRouter()

master_router.include_router(login.router)
master_router.include_router(registration.router)