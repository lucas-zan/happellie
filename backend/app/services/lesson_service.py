from __future__ import annotations

from app.domain.interfaces.analytics import CostTracker
from app.domain.interfaces.lesson import ContentRepository, LessonGenerator
from app.domain.interfaces.planning import LessonPlanner
from app.domain.interfaces.session import SessionRepository
from app.domain.interfaces.tts import TextToSpeechProvider
from app.domain.interfaces.vocab import VocabRepository
from app.schemas.lesson import LessonRequest, LessonResponse
from app.schemas.profile import ProfileSnapshot
from app.infra.validation.step_validator import validate_steps


class LessonService:
    def __init__(
        self,
        content_repo: ContentRepository,
        session_repo: SessionRepository,
        vocab_repo: VocabRepository,
        lesson_planner: LessonPlanner,
        fallback_lesson_planner: LessonPlanner,
        ai_lesson_generator: LessonGenerator,
        fallback_lesson_generator: LessonGenerator,
        tts_provider: TextToSpeechProvider,
        cost_tracker: CostTracker,
        enable_fallback: bool = True,
    ) -> None:
        self._content_repo = content_repo
        self._session_repo = session_repo
        self._vocab_repo = vocab_repo
        self._lesson_planner = lesson_planner
        self._fallback_lesson_planner = fallback_lesson_planner
        self._ai_lesson_generator = ai_lesson_generator
        self._fallback_lesson_generator = fallback_lesson_generator
        self._tts_provider = tts_provider
        self._cost_tracker = cost_tracker
        self._enable_fallback = enable_fallback

    def plan_next_lesson(self, payload: LessonRequest) -> LessonResponse:
        profile = self._session_repo.get_profile(payload.student_id)
        profile = self._apply_story_state(profile, payload.student_id)
        vocab_bank = self._vocab_repo.get_by_keys(payload.requested_vocab) if payload.requested_vocab else self._vocab_repo.list_vocab()
        try:
            blueprint = self._lesson_planner.plan(payload, profile, vocab_bank)
        except Exception as exc:
            if not self._enable_fallback:
                raise
            blueprint = self._fallback_lesson_planner.plan(payload, profile, vocab_bank)
            self._cost_tracker.record(
                "lesson_plan_fallback",
                count=1,
                metadata={"student_id": payload.student_id, "provider": "local", "error": str(exc)[:180]},
            )
        cache_key = blueprint.cache_key() if not payload.force_regenerate else ""
        if cache_key:
            cached = self._content_repo.get_cached_lesson(cache_key)
            if cached:
                self._cost_tracker.record(
                    "lesson_cache_hit",
                    count=1,
                    metadata={"student_id": payload.student_id, "provider": "local", "lesson_type": payload.lesson_type},
                )
                return LessonResponse(lesson=cached, source="cache", blueprint=blueprint)

        try:
            lesson = self._ai_lesson_generator.generate(blueprint)
        except Exception as exc:
            if not self._enable_fallback:
                raise
            lesson = self._fallback_lesson_generator.generate(blueprint)
            self._cost_tracker.record(
                "lesson_generate_fallback",
                count=1,
                metadata={"student_id": payload.student_id, "provider": "local", "error": str(exc)[:180]},
            )

        # Validate step-based payloads (v3). Keep pages compatibility.
        lesson.steps = validate_steps(getattr(lesson, "steps", []) or [])

        for page in lesson.pages:
            for component in page.components:
                if component.type not in {"word_card", "choice_quiz", "repeat_prompt", "hero_banner", "story_panel", "encounter_card"}:
                    continue
                text = (
                    component.payload.get("text")
                    or component.payload.get("question")
                    or component.prompt
                    or component.title
                )
                audio_path = self._tts_provider.synthesize(str(text))
                if audio_path:
                    component.payload["audio_path"] = audio_path
        if cache_key:
            self._content_repo.save_cached_lesson(cache_key, lesson)
        return LessonResponse(lesson=lesson, source="generated", blueprint=blueprint)

    def _apply_story_state(self, profile: ProfileSnapshot | None, student_id: str) -> ProfileSnapshot | None:
        state = self._session_repo.get_story_state(student_id)
        if not state:
            return profile
        if profile is None:
            profile = ProfileSnapshot(student_id=student_id)
        profile.story_arc_key = str(state.get("arc_key") or profile.story_arc_key)
        profile.story_chapter_key = str(state.get("chapter_key") or profile.story_chapter_key)
        profile.story_episode_index = int(state.get("episode_index") or profile.story_episode_index or 1)
        profile.story_last_choice_key = str(state.get("last_choice_key") or profile.story_last_choice_key)
        profile.story_last_choice_tag = str(state.get("last_choice_tag") or profile.story_last_choice_tag)
        profile.story_last_scene = str(state.get("last_scene") or profile.story_last_scene)
        hooks = state.get("unresolved_hooks") or []
        if hooks and isinstance(hooks, list):
            profile.story_next_hook = str(hooks[0])
        return profile
