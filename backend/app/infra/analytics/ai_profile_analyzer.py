from __future__ import annotations

from app.domain.interfaces.analytics import CostTracker, ProfileAnalyzer
from app.domain.interfaces.llm import StructuredLLMClient
from app.schemas.profile import ProfileSnapshot, RecentSessionSummary, SessionSignals


class AIProfileAnalyzer(ProfileAnalyzer):
    def __init__(
        self,
        llm: StructuredLLMClient,
        model: str,
        cost_tracker: CostTracker,
        provider_name: str,
        input_cost_per_million: float = 0.0,
        output_cost_per_million: float = 0.0,
        temperature: float = 0.2,
    ) -> None:
        self._llm = llm
        self._model = model
        self._cost_tracker = cost_tracker
        self._provider_name = provider_name
        self._input_cost_per_million = input_cost_per_million
        self._output_cost_per_million = output_cost_per_million
        self._temperature = temperature

    def recompute(
        self,
        student_id: str,
        signals: SessionSignals,
        previous_profile: ProfileSnapshot | None = None,
        recent_sessions: list[RecentSessionSummary] | None = None,
    ) -> ProfileSnapshot:
        schema = {
            "type": "object",
            "properties": {
                "weak_vocab_tags": {"type": "array", "items": {"type": "string"}},
                "weak_skill_tags": {"type": "array", "items": {"type": "string"}},
                "interest_tags": {"type": "array", "items": {"type": "string"}},
                "preferred_themes": {"type": "array", "items": {"type": "string"}},
                "recommended_session_minutes": {"type": "integer"},
                "motivation_level": {"type": "string"},
                "frustration_risk": {"type": "string"},
                "current_level": {"type": "string"},
                "latest_focus": {"type": "array", "items": {"type": "string"}},
                "recommended_vocab_keys": {"type": "array", "items": {"type": "string"}},
                "summary_note": {"type": "string"},
                "story_arc_key": {"type": "string"},
                "story_episode_index": {"type": "integer"},
                "story_last_scene": {"type": "string"},
                "story_next_hook": {"type": "string"},
                "story_characters": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "weak_vocab_tags",
                "weak_skill_tags",
                "interest_tags",
                "preferred_themes",
                "recommended_session_minutes",
                "motivation_level",
                "frustration_risk",
                "current_level",
                "latest_focus",
                "recommended_vocab_keys",
                "summary_note",
                "story_arc_key",
                "story_episode_index",
                "story_last_scene",
                "story_next_hook",
                "story_characters",
            ],
            "additionalProperties": False,
        }
        user_prompt = (
            "Update the learner profile for HappyEllie.\n"
            f"Current student id: {student_id}\n"
            f"Previous profile: {(previous_profile.model_dump() if previous_profile else {})}\n"
            f"New session signals: {signals.model_dump()}\n"
            f"Recent sessions: {[item.model_dump() for item in (recent_sessions or [])]}\n"
            "Rules: the child is a beginner; keep recommendations short and specific; return concise tags only; "
            "recommended_session_minutes should stay between 4 and 10. "
            "Preserve story continuity by updating the current arc, episode number, latest scene, next hook, and memorable characters."
        )
        result = self._llm.generate_json(
            system_prompt="You analyze a child's English-learning progress for a playful pet-learning app. Return JSON only.",
            user_prompt=user_prompt,
            schema_name="profile_snapshot",
            schema=schema,
            model=self._model,
            temperature=self._temperature,
        )
        self._cost_tracker.record(
            "ai_profile_analyze",
            count=1,
            cost_cents=self._estimate_cost_cents(result.prompt_tokens, result.completion_tokens),
            metadata={
                "provider": self._provider_name,
                "model": result.model,
                "prompt_tokens": result.prompt_tokens,
                "completion_tokens": result.completion_tokens,
                "student_id": student_id,
            },
        )
        data = result.data
        return ProfileSnapshot(
            student_id=student_id,
            weak_vocab_tags=[str(item) for item in data.get("weak_vocab_tags", [])][:4],
            weak_skill_tags=[str(item) for item in data.get("weak_skill_tags", [])][:4],
            interest_tags=[str(item) for item in data.get("interest_tags", [])][:4],
            preferred_themes=[str(item) for item in data.get("preferred_themes", [])][:3] or ["feed_rabbit"],
            recommended_session_minutes=max(4, min(10, int(data.get("recommended_session_minutes") or 6))),
            motivation_level=str(data.get("motivation_level") or "medium"),
            frustration_risk=str(data.get("frustration_risk") or "low"),
            current_level=str(data.get("current_level") or "starter"),
            latest_focus=[str(item) for item in data.get("latest_focus", [])][:3],
            recommended_vocab_keys=[str(item) for item in data.get("recommended_vocab_keys", [])][:6],
            summary_note=str(data.get("summary_note") or "AI profile update."),
            story_arc_key=str(data.get("story_arc_key") or "snack_scouts"),
            story_episode_index=max(1, int(data.get("story_episode_index") or 1)),
            story_last_scene=str(data.get("story_last_scene") or signals.story_last_scene or "Ellie finished a tiny mission."),
            story_next_hook=str(data.get("story_next_hook") or signals.story_next_hook or "A new creature appears near the next snack trail."),
            story_characters=[str(item) for item in data.get("story_characters", [])][:6] or list(signals.encountered_characters)[:6],
        )

    def _estimate_cost_cents(self, prompt_tokens: int, completion_tokens: int) -> int:
        total_currency = (
            prompt_tokens * self._input_cost_per_million + completion_tokens * self._output_cost_per_million
        ) / 1_000_000
        return int(round(total_currency * 100))
