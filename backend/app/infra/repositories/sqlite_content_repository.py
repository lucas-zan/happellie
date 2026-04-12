import json

from app.domain.interfaces.lesson import ContentRepository
from app.infra.db.connection import SqliteConnectionFactory
from app.schemas.lesson import LessonPackage


class SqliteContentRepository(ContentRepository):
    def __init__(self, connection_factory: SqliteConnectionFactory) -> None:
        self._connection_factory = connection_factory

    def get_cached_lesson(self, cache_key: str) -> LessonPackage | None:
        with self._connection_factory.connect() as conn:
            row = conn.execute(
                "SELECT lesson_json FROM lesson_cache WHERE cache_key = ?",
                (cache_key,),
            ).fetchone()
        if not row:
            return None
        return LessonPackage.model_validate(json.loads(row["lesson_json"]))

    def save_cached_lesson(self, cache_key: str, lesson: LessonPackage) -> None:
        with self._connection_factory.connect() as conn:
            conn.execute(
                "REPLACE INTO lesson_cache (cache_key, lesson_json) VALUES (?, ?)",
                (cache_key, lesson.model_dump_json()),
            )
