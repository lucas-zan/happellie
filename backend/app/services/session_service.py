from __future__ import annotations

from app.domain.interfaces.analytics import CostTracker, ProfileAnalyzer
from app.domain.interfaces.pet import PetRepository
from app.domain.interfaces.session import SessionRepository
from app.schemas.profile import SessionSignals
from app.schemas.session import SessionCompleteRequest, SessionCompleteResponse


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
