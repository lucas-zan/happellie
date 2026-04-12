from fastapi import APIRouter, Depends

from app.core.container import get_session_service
from app.schemas.session import SessionCompleteRequest, SessionCompleteResponse
from app.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/complete", response_model=SessionCompleteResponse)
def complete_session(
    payload: SessionCompleteRequest,
    service: SessionService = Depends(get_session_service),
) -> SessionCompleteResponse:
    return service.complete_session(payload)
