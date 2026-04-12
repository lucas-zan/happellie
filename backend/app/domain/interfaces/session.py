from __future__ import annotations

from typing import Protocol

from app.schemas.profile import ProfileSnapshot, RecentSessionSummary
from app.schemas.session import SessionCompleteRequest


class SessionRepository(Protocol):
    def create_or_update_session(self, payload: SessionCompleteRequest) -> None:
        ...

    def get_profile(self, student_id: str) -> ProfileSnapshot | None:
        ...

    def save_profile(self, profile: ProfileSnapshot) -> None:
        ...

    def list_recent_sessions(self, student_id: str, limit: int = 8) -> list[RecentSessionSummary]:
        ...


class UsageStatsRepository(Protocol):
    def get_usage_overview(self) -> dict:
        ...
