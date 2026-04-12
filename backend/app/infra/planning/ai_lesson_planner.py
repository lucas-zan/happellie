from __future__ import annotations

from app.domain.interfaces.analytics import CostTracker
from app.domain.interfaces.llm import StructuredLLMClient
from app.domain.interfaces.planning import LessonPlanner
from app.schemas.lesson import LessonBlueprint, LessonBlueprintPage, LessonRequest, StoryThread, VocabItem
from app.schemas.profile import ProfileSnapshot


class AILessonPlanner(LessonPlanner):
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

    def plan(
        self,
        request: LessonRequest,
        profile: ProfileSnapshot | None,
        available_vocab: list[VocabItem],
    ) -> LessonBlueprint:
        schema = {
            "type": "object",
            "properties": {
                "theme": {"type": "string"},
                "title": {"type": "string"},
                "focus_tags": {"type": "array", "items": {"type": "string"}},
                "selected_vocab_keys": {"type": "array", "items": {"type": "string"}},
                "teacher_note": {"type": "string"},
                "rewards": {
                    "type": "object",
                    "properties": {
                        "coins": {"type": "integer"},
                        "food": {"type": "integer"},
                    },
                    "required": ["coins", "food"],
                    "additionalProperties": False,
                },
                "story": {
                    "type": "object",
                    "properties": {
                        "arc_key": {"type": "string"},
                        "episode_index": {"type": "integer"},
                        "episode_title": {"type": "string"},
                        "recap": {"type": "string"},
                        "current_mission": {"type": "string"},
                        "next_hook": {"type": "string"},
                        "characters": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "character_id": {"type": "string"},
                                    "name": {"type": "string"},
                                    "kind": {"type": "string", "enum": ["pet", "companion", "monster", "animal"]},
                                    "role": {"type": "string"},
                                    "mood": {"type": "string"},
                                },
                                "required": ["character_id", "name", "kind", "role", "mood"],
                                "additionalProperties": False,
                            },
                            "minItems": 2,
                        },
                    },
                    "required": ["arc_key", "episode_index", "episode_title", "recap", "current_mission", "next_hook", "characters"],
                    "additionalProperties": False,
                },
                "pages": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "page_id": {"type": "string"},
                            "page_type": {
                                "type": "string",
                                "enum": [
                                    "hero",
                                    "learn",
                                    "quiz",
                                    "repeat",
                                    "settlement",
                                    "feed_pet",
                                ],
                            },
                            "title": {"type": "string"},
                            "goal": {"type": "string"},
                            "component_types": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": [
                                        "hero_banner",
                                        "story_panel",
                                        "encounter_card",
                                        "word_card",
                                        "choice_quiz",
                                        "repeat_prompt",
                                        "reward_panel",
                                        "feed_panel",
                                        "pet_reaction",
                                    ],
                                },
                                "minItems": 1,
                            },
                            "payload_hints": {"type": "object"},
                        },
                        "required": ["page_id", "page_type", "title", "goal", "component_types", "payload_hints"],
                        "additionalProperties": False,
                    },
                    "minItems": 5,
                },
            },
            "required": ["theme", "title", "focus_tags", "selected_vocab_keys", "teacher_note", "rewards", "story", "pages"],
            "additionalProperties": False,
        }
        catalog = [
            {
                "key": item.key,
                "text": item.text,
                "meaning": item.meaning,
                "category": item.category,
                "difficulty": item.difficulty,
                "tags": item.tags,
                "sample_sentence": item.sample_sentence,
            }
            for item in available_vocab
        ]
        profile_payload = profile.model_dump() if profile else {}
        user_prompt = (
            "Plan one tiny lesson blueprint for a young beginner learning English.\n"
            f"Request: {request.model_dump_json()}\n"
            f"Current profile: {profile_payload}\n"
            f"Available vocab catalog: {catalog}\n"
            "Rules: choose 3 or 4 vocabulary items, keep the lesson playful, short, and pet-themed. "
            "Always include exactly these page types in a logical order: hero, learn, quiz, repeat, settlement, feed_pet. "
            "Continue the existing story arc when profile story fields are present. "
            "Include one cute helper animal and one soft, non-scary monster or rival creature. "
            "Use component_types that fit the page_type. "
            "Only use selected_vocab_keys from the provided catalog."
        )
        result = self._llm.generate_json(
            system_prompt="You are HappyEllie's curriculum planner. Always return concise JSON only.",
            user_prompt=user_prompt,
            schema_name="lesson_blueprint",
            schema=schema,
            model=self._model,
            temperature=self._temperature,
        )
        self._cost_tracker.record(
            "ai_plan",
            count=1,
            cost_cents=self._estimate_cost_cents(result.prompt_tokens, result.completion_tokens),
            metadata={
                "provider": self._provider_name,
                "model": result.model,
                "prompt_tokens": result.prompt_tokens,
                "completion_tokens": result.completion_tokens,
                "student_id": request.student_id,
            },
        )
        data = result.data
        selected_keys = [key for key in data.get("selected_vocab_keys", []) if isinstance(key, str)]
        selected_vocab = [item for item in available_vocab if item.key in selected_keys]
        if len(selected_vocab) < 3:
            selected_vocab = available_vocab[:4]
        pages = [LessonBlueprintPage.model_validate(item) for item in data.get("pages", [])]
        return LessonBlueprint(
            student_id=request.student_id,
            lesson_type=request.lesson_type,
            theme=str(data.get("theme") or "feed_rabbit"),
            level_hint=request.level_hint,
            title=str(data.get("title") or "HappyEllie lesson"),
            target_vocab=selected_vocab,
            focus_tags=[str(item) for item in data.get("focus_tags", [])][:4],
            rewards=data.get("rewards") or {"coins": 4, "food": 1},
            pages=pages,
            story=StoryThread.model_validate(data.get("story") or {}),
            teacher_note=str(data.get("teacher_note") or "Keep it short and friendly."),
        )

    def _estimate_cost_cents(self, prompt_tokens: int, completion_tokens: int) -> int:
        total_currency = (
            prompt_tokens * self._input_cost_per_million + completion_tokens * self._output_cost_per_million
        ) / 1_000_000
        return int(round(total_currency * 100))
