from fastapi import APIRouter

from app.api.v1.routers import dashboard, organization, documents

master_router = APIRouter()

master_router.include_router(dashboard.router)
master_router.include_router(organization.router)
master_router.include_router(documents.router)