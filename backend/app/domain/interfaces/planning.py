from __future__ import annotations

from typing import Protocol

from app.schemas.lesson import LessonBlueprint, LessonRequest, VocabItem
from app.schemas.profile import ProfileSnapshot


class LessonPlanner(Protocol):
    def plan(
        self,
        request: LessonRequest,
        profile: ProfileSnapshot | None,
        available_vocab: list[VocabItem],
    ) -> LessonBlueprint:
        ...
