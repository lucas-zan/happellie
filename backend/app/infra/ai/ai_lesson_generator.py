from __future__ import annotations

from uuid import uuid4

from app.domain.interfaces.analytics import CostTracker
from app.domain.interfaces.lesson import LessonGenerator
from app.domain.interfaces.llm import StructuredLLMClient
from app.schemas.lesson import LessonBlueprint, LessonComponent, LessonPackage, LessonPage


class AILessonGenerator(LessonGenerator):
    def __init__(
        self,
        llm: StructuredLLMClient,
        model: str,
        cost_tracker: CostTracker,
        provider_name: str,
        input_cost_per_million: float = 0.0,
        output_cost_per_million: float = 0.0,
        temperature: float = 0.3,
    ) -> None:
        self._llm = llm
        self._model = model
        self._cost_tracker = cost_tracker
        self._provider_name = provider_name
        self._input_cost_per_million = input_cost_per_million
        self._output_cost_per_million = output_cost_per_million
        self._temperature = temperature

    def generate(self, blueprint: LessonBlueprint) -> LessonPackage:
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "teacher_note": {"type": "string"},
                "estimated_minutes": {"type": "integer"},
                "pages": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "page_id": {"type": "string"},
                            "page_type": {
                                "type": "string",
                                "enum": ["hero", "learn", "quiz", "repeat", "settlement", "feed_pet"],
                            },
                            "title": {"type": "string"},
                            "instruction": {"type": "string"},
                            "completion_label": {"type": "string"},
                            "components": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "component_id": {"type": "string"},
                                        "type": {
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
                                        "title": {"type": "string"},
                                        "prompt": {"type": "string"},
                                        "payload": {"type": "object"},
                                    },
                                    "required": ["component_id", "type", "title", "prompt", "payload"],
                                    "additionalProperties": False,
                                },
                                "minItems": 1,
                            },
                        },
                        "required": ["page_id", "page_type", "title", "instruction", "completion_label", "components"],
                        "additionalProperties": False,
                    },
                    "minItems": len(blueprint.pages),
                },
                "reward_preview": {
                    "type": "object",
                    "properties": {
                        "coins": {"type": "integer"},
                        "food": {"type": "integer"},
                    },
                    "required": ["coins", "food"],
                    "additionalProperties": False,
                },
            },
            "required": ["title", "teacher_note", "estimated_minutes", "pages", "reward_preview"],
            "additionalProperties": False,
        }
        prompt = (
            "Generate one final page-based lesson package for HappyEllie.\n"
            f"Blueprint: {blueprint.model_dump()}\n"
            "Rules: keep the child-facing text extremely short and cheerful. "
            "Do not invent new page types or component types. "
            "story_panel payload should contain recap, mission, and companion_name. "
            "encounter_card payload should contain monster_name, companion_name, and challenge. "
            "word_card payload must contain items as a list of {word, meaning}. "
            "choice_quiz payload must contain question, options, answer. "
            "repeat_prompt payload must contain text. "
            "reward_panel payload must contain coins and food. "
            "feed_panel payload must contain food_type and quantity. "
            "pet_reaction payload should contain emotion. "
            "Only use vocabulary from target_vocab."
        )
        result = self._llm.generate_json(
            system_prompt="You write tiny structured game pages for young children. Return JSON only.",
            user_prompt=prompt,
            schema_name="lesson_package",
            schema=schema,
            model=self._model,
            temperature=self._temperature,
        )
        self._cost_tracker.record(
            "ai_generate",
            count=1,
            cost_cents=self._estimate_cost_cents(result.prompt_tokens, result.completion_tokens),
            metadata={
                "provider": self._provider_name,
                "model": result.model,
                "prompt_tokens": result.prompt_tokens,
                "completion_tokens": result.completion_tokens,
                "student_id": blueprint.student_id,
            },
        )
        data = result.data
        pages = [LessonPage.model_validate(item) for item in data.get("pages", [])]
        return LessonPackage(
            lesson_id=f"lesson-{uuid4().hex[:8]}",
            student_id=blueprint.student_id,
            title=str(data.get("title") or blueprint.title),
            theme=blueprint.theme,
            estimated_minutes=max(4, min(10, int(data.get("estimated_minutes") or 6))),
            vocab=[item.text for item in blueprint.target_vocab],
            target_vocab_items=blueprint.target_vocab,
            story=blueprint.story,
            pages=pages,
            reward_preview=data.get("reward_preview") or blueprint.rewards,
            focus_tags=blueprint.focus_tags,
            teacher_note=str(data.get("teacher_note") or blueprint.teacher_note),
            source_model=result.model,
            debug_metadata={"blueprint_id": blueprint.blueprint_id, "generator": result.model},
        )

    def _estimate_cost_cents(self, prompt_tokens: int, completion_tokens: int) -> int:
        total_currency = (
            prompt_tokens * self._input_cost_per_million + completion_tokens * self._output_cost_per_million
        ) / 1_000_000
        return int(round(total_currency * 100))
