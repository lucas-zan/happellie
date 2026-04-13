from __future__ import annotations

from app.domain.interfaces.session import SessionRepository
from app.schemas.profile import ProfileSnapshot


class ProfileService:
    def __init__(self, session_repo: SessionRepository) -> None:
        self._session_repo = session_repo

    def get_profile(self, student_id: str) -> ProfileSnapshot:
        profile = self._session_repo.get_profile(student_id)
        return profile or ProfileSnapshot(student_id=student_id)

    def get_story_events(self, student_id: str, limit: int = 20) -> list[dict]:
        return self._session_repo.list_story_events(student_id, limit=limit)
