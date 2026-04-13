from __future__ import annotations

import json

from app.domain.interfaces.session import SessionRepository, UsageStatsRepository
from app.infra.db.connection import SqliteConnectionFactory
from app.schemas.profile import ProfileSnapshot, RecentSessionSummary
from app.schemas.session import LearningEvent, SessionCompleteRequest


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

    def save_learning_events(self, events: list[LearningEvent]) -> int:
        if not events:
            return 0
        with self._connection_factory.connect() as conn:
            conn.executemany(
                """
                INSERT INTO learning_events (
                    event_id, session_id, student_id, lesson_id, step_id, template_id, event_type, payload_json, event_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        item.event_id,
                        item.session_id,
                        item.student_id,
                        item.lesson_id,
                        item.step_id,
                        item.template_id,
                        item.event_type,
                        json.dumps(item.payload, ensure_ascii=False),
                        item.timestamp or None,
                    )
                    for item in events
                ],
            )
        return len(events)

    def upsert_vocab_mastery(self, student_id: str, entries: list[dict]) -> int:
        if not entries:
            return 0
        with self._connection_factory.connect() as conn:
            for item in entries:
                vocab_key = str(item.get("vocab_key") or "").strip()
                if not vocab_key:
                    continue
                attempts = int(item.get("attempts") or 1)
                correct_count = int(item.get("correct_count") or 0)
                wrong_count = int(item.get("wrong_count") or 0)
                last_result_correct = 1 if bool(item.get("last_result_correct")) else 0
                last_score = int(item.get("last_score") or 0)
                conn.execute(
                    """
                    INSERT INTO vocab_mastery (
                        student_id, vocab_key, attempts, correct_count, wrong_count, last_result_correct, last_score, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(student_id, vocab_key) DO UPDATE SET
                        attempts = attempts + excluded.attempts,
                        correct_count = correct_count + excluded.correct_count,
                        wrong_count = wrong_count + excluded.wrong_count,
                        last_result_correct = excluded.last_result_correct,
                        last_score = excluded.last_score,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (student_id, vocab_key, attempts, correct_count, wrong_count, last_result_correct, last_score),
                )
        return len(entries)

    def list_weak_vocab_keys(self, student_id: str, limit: int = 6) -> list[str]:
        with self._connection_factory.connect() as conn:
            rows = conn.execute(
                """
                SELECT vocab_key
                FROM vocab_mastery
                WHERE student_id = ? AND attempts >= 1
                ORDER BY (
                            ((wrong_count * 1.0) / CASE WHEN attempts = 0 THEN 1 ELSE attempts END) * 0.75
                            + (MIN(14.0, MAX(0.0, julianday('now') - julianday(updated_at))) / 14.0) * 0.25
                         ) DESC,
                         wrong_count DESC,
                         attempts DESC,
                         updated_at DESC
                LIMIT ?
                """,
                (student_id, limit),
            ).fetchall()
        return [str(row["vocab_key"]) for row in rows if row["vocab_key"]]

    def save_session_steps(self, student_id: str, lesson_id: str, steps: list[dict]) -> int:
        if not steps:
            return 0
        with self._connection_factory.connect() as conn:
            conn.executemany(
                """
                INSERT INTO session_steps (
                    student_id, lesson_id, step_id, template_id, correct, score, duration_ms, details_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        student_id,
                        lesson_id,
                        str(item.get("step_id") or ""),
                        str(item.get("template_id") or ""),
                        None
                        if item.get("correct") is None
                        else (1 if bool(item.get("correct")) else 0),
                        int(item.get("score") or 0),
                        int(item.get("duration_ms") or 0),
                        json.dumps(item.get("details") or {}, ensure_ascii=False),
                    )
                    for item in steps
                ],
            )
        return len(steps)

    def save_story_state(self, student_id: str, state: dict) -> None:
        with self._connection_factory.connect() as conn:
            conn.execute(
                """
                INSERT INTO story_state (
                    student_id, arc_key, chapter_key, episode_index, last_choice_key, last_choice_tag, unresolved_hooks_json, state_json, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(student_id) DO UPDATE SET
                    arc_key = excluded.arc_key,
                    chapter_key = excluded.chapter_key,
                    episode_index = excluded.episode_index,
                    last_choice_key = excluded.last_choice_key,
                    last_choice_tag = excluded.last_choice_tag,
                    unresolved_hooks_json = excluded.unresolved_hooks_json,
                    state_json = excluded.state_json,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    student_id,
                    str(state.get("arc_key") or "snack_scouts"),
                    str(state.get("chapter_key") or "chapter_1"),
                    int(state.get("episode_index") or 1),
                    str(state.get("last_choice_key") or ""),
                    str(state.get("last_choice_tag") or ""),
                    json.dumps(state.get("unresolved_hooks") or [], ensure_ascii=False),
                    json.dumps(state or {}, ensure_ascii=False),
                ),
            )

    def get_story_state(self, student_id: str) -> dict | None:
        with self._connection_factory.connect() as conn:
            row = conn.execute(
                """
                SELECT arc_key, chapter_key, episode_index, last_choice_key, last_choice_tag, unresolved_hooks_json, state_json
                FROM story_state
                WHERE student_id = ?
                """,
                (student_id,),
            ).fetchone()
        if not row:
            return None
        state = json.loads(row["state_json"] or "{}")
        # Ensure top-level keys exist even if stored state_json is minimal.
        state.setdefault("arc_key", row["arc_key"] or "snack_scouts")
        state.setdefault("chapter_key", row["chapter_key"] or "chapter_1")
        state.setdefault("episode_index", row["episode_index"] or 1)
        state.setdefault("last_choice_key", row["last_choice_key"] or "")
        state.setdefault("last_choice_tag", row["last_choice_tag"] or "")
        state.setdefault("unresolved_hooks", json.loads(row["unresolved_hooks_json"] or "[]"))
        return state

    def save_story_event(self, student_id: str, lesson_id: str, event: dict) -> None:
        with self._connection_factory.connect() as conn:
            conn.execute(
                """
                INSERT INTO story_events (student_id, lesson_id, event_type, event_json)
                VALUES (?, ?, ?, ?)
                """,
                (
                    student_id,
                    lesson_id,
                    str(event.get("event_type") or "story_progress"),
                    json.dumps(event or {}, ensure_ascii=False),
                ),
            )

    def list_story_events(self, student_id: str, limit: int = 30) -> list[dict]:
        with self._connection_factory.connect() as conn:
            rows = conn.execute(
                """
                SELECT lesson_id, event_type, event_json, created_at
                FROM story_events
                WHERE student_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (student_id, limit),
            ).fetchall()
        return [
            {
                "lesson_id": row["lesson_id"],
                "event_type": row["event_type"],
                "event": json.loads(row["event_json"] or "{}"),
                "created_at": row["created_at"] or "",
            }
            for row in rows
        ]
