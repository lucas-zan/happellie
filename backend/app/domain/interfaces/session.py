from __future__ import annotations

from typing import Protocol

from app.schemas.profile import ProfileSnapshot, RecentSessionSummary
from app.schemas.session import LearningEvent, SessionCompleteRequest


class SessionRepository(Protocol):
    def create_or_update_session(self, payload: SessionCompleteRequest) -> None:
        ...

    def get_profile(self, student_id: str) -> ProfileSnapshot | None:
        ...

    def save_profile(self, profile: ProfileSnapshot) -> None:
        ...

    def list_recent_sessions(self, student_id: str, limit: int = 8) -> list[RecentSessionSummary]:
        ...

    def save_learning_events(self, events: list[LearningEvent]) -> int:
        ...

    def upsert_vocab_mastery(self, student_id: str, entries: list[dict]) -> int:
        ...

    def list_weak_vocab_keys(self, student_id: str, limit: int = 6) -> list[str]:
        ...

    def save_session_steps(self, student_id: str, lesson_id: str, steps: list[dict]) -> int:
        ...

    def save_story_state(self, student_id: str, state: dict) -> None:
        ...

    def get_story_state(self, student_id: str) -> dict | None:
        ...

    def save_story_event(self, student_id: str, lesson_id: str, event: dict) -> None:
        ...

    def list_story_events(self, student_id: str, limit: int = 30) -> list[dict]:
        ...


class UsageStatsRepository(Protocol):
    def get_usage_overview(self) -> dict:
        ...
