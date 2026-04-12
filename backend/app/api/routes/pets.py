from fastapi import APIRouter, Depends

from app.core.container import get_pet_service
from app.schemas.pet import FeedPetRequest, PetFeedResponse, PetSummary
from app.services.pet_service import PetService

router = APIRouter(prefix="/pets", tags=["pets"])


@router.get("/{student_id}", response_model=PetSummary)
def get_pet(student_id: str, service: PetService = Depends(get_pet_service)) -> PetSummary:
    return service.get_pet_summary(student_id)


@router.post("/feed", response_model=PetFeedResponse)
def feed_pet(
    payload: FeedPetRequest,
    service: PetService = Depends(get_pet_service),
) -> PetFeedResponse:
    return service.feed_pet(payload)
