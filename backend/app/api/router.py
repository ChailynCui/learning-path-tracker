from fastapi import APIRouter

from app.api.routes import archives, backup, dashboard, paths

api_router = APIRouter(prefix="/api")
api_router.include_router(paths.router, prefix="/paths", tags=["paths"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(archives.router, prefix="/archives", tags=["archives"])
api_router.include_router(backup.router, prefix="/backup", tags=["backup"])
