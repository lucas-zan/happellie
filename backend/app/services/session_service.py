from __future__ import annotations

from collections import defaultdict

from app.domain.interfaces.analytics import CostTracker, ProfileAnalyzer
from app.domain.interfaces.pet import PetRepository
from app.domain.interfaces.session import SessionRepository
from app.schemas.profile import SessionSignals
from app.schemas.session import SessionCompleteRequest, SessionCompleteResponse, SessionEventsRequest, SessionEventsResponse


class SessionService:
    def __init__(
        self,
        session_repo: SessionRepository,
        pet_repo: PetRepository,
        ai_profile_analyzer: ProfileAnalyzer,
        fallback_profile_analyzer: ProfileAnalyzer,
        cost_tracker: CostTracker,
        recent_sessions_limit: int = 8,
        enable_fallback: bool = True,
    ) -> None:
        self._session_repo = session_repo
        self._pet_repo = pet_repo
        self._ai_profile_analyzer = ai_profile_analyzer
        self._fallback_profile_analyzer = fallback_profile_analyzer
        self._cost_tracker = cost_tracker
        self._recent_sessions_limit = recent_sessions_limit
        self._enable_fallback = enable_fallback

    def complete_session(self, payload: SessionCompleteRequest) -> SessionCompleteResponse:
        self._session_repo.create_or_update_session(payload)
        self._session_repo.save_session_steps(
            payload.student_id,
            payload.lesson_id,
            [item.model_dump() for item in payload.step_results],
        )
        mastery_entries = self._collect_vocab_mastery_entries(payload)
        if mastery_entries:
            self._session_repo.upsert_vocab_mastery(payload.student_id, mastery_entries)
        pet = self._pet_repo.get_or_create_pet(payload.student_id)
        pet.coins += payload.earned_coins
        pet.food_inventory["basic_food"] = pet.food_inventory.get("basic_food", 0) + payload.earned_food
        self._pet_repo.save_pet(pet)

        signals = SessionSignals(
            duration_seconds=payload.duration_seconds,
            correct_count=sum(1 for item in payload.block_results if item.correct),
            wrong_count=sum(1 for item in payload.block_results if not item.correct),
            speaking_attempts=sum(1 for item in payload.block_results if item.block_type == "repeat_prompt"),
            preferred_block_types=[item.block_type for item in payload.block_results],
            completed_blocks=len(payload.block_results),
            total_blocks=len(payload.block_results),
            score=payload.total_score,
            earned_food=payload.earned_food,
            earned_coins=payload.earned_coins,
            story_arc_key=payload.story_arc_key,
            story_episode_index=payload.story_episode_index,
            story_last_scene=payload.story_last_scene,
            story_next_hook=payload.story_next_hook,
            encountered_characters=payload.encountered_characters,
        )
        previous_profile = self._session_repo.get_profile(payload.student_id)
        recent_sessions = self._session_repo.list_recent_sessions(payload.student_id, limit=self._recent_sessions_limit)
        try:
            profile = self._ai_profile_analyzer.recompute(payload.student_id, signals, previous_profile, recent_sessions)
        except Exception as exc:
            if not self._enable_fallback:
                raise
            profile = self._fallback_profile_analyzer.recompute(payload.student_id, signals, previous_profile, recent_sessions)
            self._cost_tracker.record(
                "profile_fallback",
                count=1,
                metadata={"student_id": payload.student_id, "provider": "local", "error": str(exc)[:180]},
            )
        weak_vocab = self._session_repo.list_weak_vocab_keys(payload.student_id, limit=6)
        profile.story_chapter_key = self._chapter_by_episode(payload.story_episode_index)
        if weak_vocab:
            profile.weak_vocab_tags = weak_vocab[:6]
            profile.recommended_vocab_keys = weak_vocab[:6]
            if weak_vocab[0] not in profile.latest_focus:
                profile.latest_focus = [weak_vocab[0], *profile.latest_focus][:3]
        story_choice = self._extract_story_choice(payload)
        if story_choice:
            choice_text = str(story_choice.get("chosen_text") or story_choice.get("chosen_key") or "a brave path")
            consequence = str(story_choice.get("consequence_tag") or "adventure")
            profile.story_last_scene = f"Player chose: {choice_text}"
            profile.story_next_hook = f"Because of the {consequence} choice, a new challenge appears next lesson."
            profile.story_last_choice_key = str(story_choice.get("chosen_key") or "")
            profile.story_last_choice_tag = consequence
            profile.story_chapter_key = self._chapter_by_episode(payload.story_episode_index)
            if consequence not in profile.interest_tags:
                profile.interest_tags = [consequence, *profile.interest_tags][:5]
            profile.summary_note = f"Recent branch: {choice_text} ({consequence})"
        self._session_repo.save_story_state(
            payload.student_id,
            self._build_story_state(payload, profile, story_choice),
        )
        self._session_repo.save_story_event(
            payload.student_id,
            payload.lesson_id,
            {
                "event_type": "lesson_completed",
                "story_arc_key": payload.story_arc_key,
                "chapter_key": self._chapter_by_episode(payload.story_episode_index),
                "episode_index": payload.story_episode_index,
                "last_scene": payload.story_last_scene,
                "next_hook": payload.story_next_hook,
                "choice": story_choice or {},
            },
        )
        self._session_repo.save_profile(profile)
        self._cost_tracker.record("session_complete", count=1, metadata={"student_id": payload.student_id, "provider": "local"})

        return SessionCompleteResponse(
            next_recommendation={
                "lesson_type": "pet_feeding",
                "focus": profile.latest_focus or profile.weak_vocab_tags[:2] or ["food"],
                "theme": profile.preferred_themes[:1] or ["feed_rabbit"],
                "recommended_vocab_keys": profile.recommended_vocab_keys[:4],
                "story_arc_key": profile.story_arc_key,
                "story_episode_index": profile.story_episode_index,
                "story_next_hook": profile.story_next_hook,
            },
            updated_profile=profile.model_dump(),
        )

    def record_events(self, payload: SessionEventsRequest) -> SessionEventsResponse:
        saved = self._session_repo.save_learning_events(payload.events)
        if saved:
            self._cost_tracker.record(
                "learning_events",
                count=saved,
                metadata={"student_id": payload.student_id, "session_id": payload.session_id, "provider": "local"},
            )
        return SessionEventsResponse(status="ok", saved_count=saved)

    def _collect_vocab_mastery_entries(self, payload: SessionCompleteRequest) -> list[dict]:
        aggregate: dict[str, dict] = defaultdict(
            lambda: {
                "vocab_key": "",
                "attempts": 0,
                "correct_count": 0,
                "wrong_count": 0,
                "last_result_correct": False,
                "last_score": 0,
            }
        )
        # Prefer v3 step results where details include explicit keys.
        for item in payload.step_results:
            details = item.details or {}
            candidates = []
            for key_name in ("correct_key", "selected_key", "audio_text", "word", "target_word"):
                value = details.get(key_name)
                if isinstance(value, str) and value.strip():
                    candidates.append(value.strip())
            if not candidates:
                continue
            vocab_key = candidates[0].lower().replace(" ", "_")
            row = aggregate[vocab_key]
            row["vocab_key"] = vocab_key
            row["attempts"] += 1
            if bool(item.correct):
                row["correct_count"] += 1
            else:
                row["wrong_count"] += 1
            row["last_result_correct"] = bool(item.correct)
            row["last_score"] = int(item.score)

        # Fallback: legacy block results
        if not aggregate:
            for item in payload.block_results:
                vocab_key = str(item.block_id or "").strip()
                if not vocab_key:
                    continue
                key = vocab_key.lower().replace(" ", "_")
                row = aggregate[key]
                row["vocab_key"] = key
                row["attempts"] += 1
                if item.correct:
                    row["correct_count"] += 1
                else:
                    row["wrong_count"] += 1
                row["last_result_correct"] = bool(item.correct)
                row["last_score"] = int(item.score)

        return list(aggregate.values())

    def _extract_story_choice(self, payload: SessionCompleteRequest) -> dict | None:
        for item in reversed(payload.step_results):
            if item.template_id != "story_choice":
                continue
            details = item.details or {}
            if details:
                return details
        return None

    def _build_story_state(self, payload: SessionCompleteRequest, profile, story_choice: dict | None) -> dict:
        return {
            "arc_key": payload.story_arc_key or getattr(profile, "story_arc_key", "snack_scouts"),
            "chapter_key": self._chapter_by_episode(payload.story_episode_index or getattr(profile, "story_episode_index", 1)),
            "episode_index": int(payload.story_episode_index or getattr(profile, "story_episode_index", 1) or 1),
            "last_choice_key": str((story_choice or {}).get("chosen_key") or ""),
            "last_choice_tag": str((story_choice or {}).get("consequence_tag") or ""),
            "unresolved_hooks": [payload.story_next_hook] if payload.story_next_hook else [],
            "last_scene": payload.story_last_scene or "",
            "updated_from": "session_complete",
        }

    def _chapter_by_episode(self, episode_index: int) -> str:
        index = int(episode_index or 1)
        if index <= 2:
            return "chapter_1"
        if index <= 4:
            return "chapter_2"
        return "chapter_3"
