from fastapi import APIRouter, Depends

from app.core.container import get_profile_service
from app.schemas.profile import ProfileSnapshot
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/{student_id}", response_model=ProfileSnapshot)
def get_profile(student_id: str, service: ProfileService = Depends(get_profile_service)) -> ProfileSnapshot:
    return service.get_profile(student_id)
