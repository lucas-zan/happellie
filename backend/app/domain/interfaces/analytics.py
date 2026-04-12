from __future__ import annotations

from typing import Protocol

from app.schemas.profile import ProfileSnapshot, RecentSessionSummary, SessionSignals


class ProfileAnalyzer(Protocol):
    def recompute(
        self,
        student_id: str,
        signals: SessionSignals,
        previous_profile: ProfileSnapshot | None = None,
        recent_sessions: list[RecentSessionSummary] | None = None,
    ) -> ProfileSnapshot:
        ...


class CostTracker(Protocol):
    def record(self, category: str, count: int = 1, cost_cents: int = 0, metadata: dict | None = None) -> None:
        ...

    def summarize(self) -> dict:
        ...
