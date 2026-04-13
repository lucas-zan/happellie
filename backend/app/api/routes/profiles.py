from fastapi import APIRouter, Depends

from app.core.container import get_profile_service
from app.schemas.profile import ProfileSnapshot
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/{student_id}", response_model=ProfileSnapshot)
def get_profile(student_id: str, service: ProfileService = Depends(get_profile_service)) -> ProfileSnapshot:
    return service.get_profile(student_id)


@router.get("/{student_id}/story-events")
def get_story_events(
    student_id: str,
    limit: int = 20,
    service: ProfileService = Depends(get_profile_service),
) -> dict:
    return {"student_id": student_id, "events": service.get_story_events(student_id, limit=max(1, min(limit, 100)))}
