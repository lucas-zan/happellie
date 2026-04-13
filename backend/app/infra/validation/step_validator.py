from __future__ import annotations

from uuid import uuid4

from pydantic import BaseModel, ValidationError

from app.schemas.lesson import GameStep

from .step_slots import (
    ChoiceBattleSlots,
    DragMatchSlots,
    EpisodeEndSlots,
    FeedPetStepSlots,
    ListenPickSlots,
    MissionBriefingSlots,
    RewardChestSlots,
    SentencePuzzleSlots,
    SpeakRepeatSlots,
    StoryChoiceSlots,
    StoryDialogueSlots,
    WordInSceneSlots,
    WordRevealSlots,
)

SLOT_VALIDATORS: dict[str, type[BaseModel]] = {
    "story_dialogue": StoryDialogueSlots,
    "story_choice": StoryChoiceSlots,
    "mission_briefing": MissionBriefingSlots,
    "word_reveal": WordRevealSlots,
    "word_in_scene": WordInSceneSlots,
    "listen_pick": ListenPickSlots,
    "drag_match": DragMatchSlots,
    "choice_battle": ChoiceBattleSlots,
    "sentence_puzzle": SentencePuzzleSlots,
    "speak_repeat": SpeakRepeatSlots,
    "reward_chest": RewardChestSlots,
    "feed_pet_step": FeedPetStepSlots,
    "episode_end": EpisodeEndSlots,
}


def make_fallback_step(*, reason: str = "invalid_step") -> GameStep:
    return GameStep(
        step_id=f"fallback-{uuid4().hex[:8]}",
        template_id="story_dialogue",
        title="A tiny story",
        slots={
            "background": "default",
            "dialogues": [
                {"character": "narrator", "mood": "neutral", "line": "Let's keep playing!"},
                {"character": "ellie", "mood": "happy", "line": "Ready for the next challenge?"},
            ],
            "fallback_reason": reason,
        },
        is_interactive=False,
    )


def validate_step(step: GameStep) -> GameStep:
    validator = SLOT_VALIDATORS.get(step.template_id)
    if validator is None:
        return make_fallback_step(reason=f"unknown_template:{step.template_id}")
    try:
        validated = validator.model_validate(step.slots)
    except ValidationError as exc:
        return make_fallback_step(reason=f"slots_invalid:{step.template_id}:{str(exc)[:120]}")

    step.slots = validated.model_dump()
    # minimal sanity defaults
    if not step.step_id:
        step.step_id = f"step-{uuid4().hex[:8]}"
    return step


def validate_steps(steps: list[GameStep]) -> list[GameStep]:
    if not steps:
        return [make_fallback_step(reason="empty_steps")]
    validated = [validate_step(step) for step in steps]
    return validated

