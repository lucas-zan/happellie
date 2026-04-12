from __future__ import annotations

from typing import Protocol

from app.schemas.lesson import LessonBlueprint, LessonPackage


class LessonGenerator(Protocol):
    def generate(self, blueprint: LessonBlueprint) -> LessonPackage:
        ...


class ContentRepository(Protocol):
    def get_cached_lesson(self, cache_key: str) -> LessonPackage | None:
        ...

    def save_cached_lesson(self, cache_key: str, lesson: LessonPackage) -> None:
        ...
