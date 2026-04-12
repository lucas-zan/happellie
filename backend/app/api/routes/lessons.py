from fastapi import APIRouter, Depends

from app.core.container import get_lesson_service
from app.schemas.lesson import LessonRequest, LessonResponse
from app.services.lesson_service import LessonService

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.post("/next", response_model=LessonResponse)
def next_lesson(
    payload: LessonRequest,
    service: LessonService = Depends(get_lesson_service),
) -> LessonResponse:
    return service.plan_next_lesson(payload)
