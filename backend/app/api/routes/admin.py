from fastapi import APIRouter, Depends

from app.core.container import get_admin_service
from app.schemas.admin import AdminOverviewResponse
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/overview", response_model=AdminOverviewResponse)
def overview(service: AdminService = Depends(get_admin_service)) -> AdminOverviewResponse:
    return service.get_overview()
