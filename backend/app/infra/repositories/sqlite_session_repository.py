from __future__ import annotations

import json

from app.domain.interfaces.session import SessionRepository, UsageStatsRepository
from app.infra.db.connection import SqliteConnectionFactory
from app.schemas.profile import ProfileSnapshot, RecentSessionSummary
from app.schemas.session import SessionCompleteRequest


class SqliteSessionRepository(SessionRepository, UsageStatsRepository):
    def __init__(self, connection_factory: SqliteConnectionFactory) -> None:
        self._connection_factory = connection_factory

    def create_or_update_session(self, payload: SessionCompleteRequest) -> None:
        wrong_count = sum(1 for item in payload.block_results if not item.correct)
        preferred_block_types = [item.block_type for item in payload.block_results]
        with self._connection_factory.connect() as conn:
            conn.execute(
                """
                INSERT INTO sessions (
                    student_id, lesson_id, duration_seconds, total_score,
                    earned_food, earned_coins, wrong_count, preferred_block_types_json, block_results_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.student_id,
                    payload.lesson_id,
                    payload.duration_seconds,
                    payload.total_score,
                    payload.earned_food,
                    payload.earned_coins,
                    wrong_count,
                    json.dumps(preferred_block_types, ensure_ascii=False),
                    json.dumps([item.model_dump() for item in payload.block_results], ensure_ascii=False),
                ),
            )

    def get_profile(self, student_id: str) -> ProfileSnapshot | None:
        with self._connection_factory.connect() as conn:
            row = conn.execute("SELECT profile_json FROM profiles WHERE student_id = ?", (student_id,)).fetchone()
        if not row:
            return None
        return ProfileSnapshot.model_validate(json.loads(row["profile_json"]))

    def save_profile(self, profile: ProfileSnapshot) -> None:
        with self._connection_factory.connect() as conn:
            conn.execute(
                "REPLACE INTO profiles (student_id, profile_json, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                (profile.student_id, profile.model_dump_json()),
            )

    def list_recent_sessions(self, student_id: str, limit: int = 8) -> list[RecentSessionSummary]:
        with self._connection_factory.connect() as conn:
            rows = conn.execute(
                """
                SELECT lesson_id, duration_seconds, total_score, earned_food, earned_coins,
                       wrong_count, preferred_block_types_json, created_at
                FROM sessions
                WHERE student_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (student_id, limit),
            ).fetchall()
        return [
            RecentSessionSummary(
                lesson_id=row["lesson_id"],
                duration_seconds=row["duration_seconds"],
                total_score=row["total_score"],
                earned_food=row["earned_food"],
                earned_coins=row["earned_coins"],
                wrong_count=row["wrong_count"] or 0,
                preferred_block_types=json.loads(row["preferred_block_types_json"] or "[]"),
                created_at=row["created_at"] or "",
            )
            for row in rows
        ]

    def get_usage_overview(self) -> dict:
        with self._connection_factory.connect() as conn:
            total = conn.execute(
                "SELECT COUNT(*) AS sessions, COALESCE(SUM(duration_seconds), 0) AS seconds FROM sessions"
            ).fetchone()
            per_student = conn.execute(
                "SELECT student_id, COUNT(*) AS sessions, COALESCE(SUM(duration_seconds), 0) AS seconds FROM sessions GROUP BY student_id ORDER BY seconds DESC"
            ).fetchall()
        return {
            "sessions": total["sessions"],
            "usage_minutes": round(total["seconds"] / 60),
            "students": [
                {
                    "student_id": row["student_id"],
                    "sessions": row["sessions"],
                    "usage_minutes": round(row["seconds"] / 60),
                }
                for row in per_student
            ],
        }
