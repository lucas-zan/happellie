from __future__ import annotations

from hashlib import sha256
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

LESSON_PACKAGE_VERSION = "lesson_package_v2"

PageType = Literal["hero", "learn", "quiz", "repeat", "settlement", "feed_pet"]
ComponentType = Literal[
    "hero_banner",
    "story_panel",
    "encounter_card",
    "word_card",
    "choice_quiz",
    "repeat_prompt",
    "reward_panel",
    "feed_panel",
    "pet_reaction",
]


class VocabItem(BaseModel):
    key: str
    text: str
    meaning: str
    kind: Literal["word", "phrase"] = "word"
    category: str = "general"
    difficulty: Literal["starter", "easy", "medium"] = "starter"
    tags: list[str] = Field(default_factory=list)
    sample_sentence: str = ""
    image_hint: str = ""


class LessonComponent(BaseModel):
    component_id: str
    type: ComponentType
    title: str = ""
    prompt: str = ""
    payload: dict = Field(default_factory=dict)


class StoryCharacter(BaseModel):
    character_id: str
    name: str
    kind: Literal["pet", "companion", "monster", "animal"]
    role: str
    mood: str = "curious"


class StoryThread(BaseModel):
    arc_key: str = "snack_scouts"
    episode_index: int = 1
    episode_title: str = "Episode 1: Snack Scouts"
    recap: str = "Ellie started a tiny snack adventure."
    current_mission: str = "Help Ellie find today's snack."
    next_hook: str = "A new friend may appear in the next lesson."
    characters: list[StoryCharacter] = Field(default_factory=list)


class LessonPage(BaseModel):
    page_id: str
    page_type: PageType
    title: str
    instruction: str = ""
    completion_label: str = "Next"
    components: list[LessonComponent] = Field(default_factory=list)


class LessonBlueprintPage(BaseModel):
    page_id: str
    page_type: PageType
    title: str
    goal: str
    component_types: list[ComponentType] = Field(default_factory=list)
    payload_hints: dict = Field(default_factory=dict)


class LessonBlueprint(BaseModel):
    blueprint_id: str = Field(default_factory=lambda: f"blueprint-{uuid4().hex[:8]}")
    student_id: str
    lesson_type: str = "pet_feeding"
    theme: str = "feed_rabbit"
    level_hint: str = "starter"
    title: str
    target_vocab: list[VocabItem]
    focus_tags: list[str] = Field(default_factory=list)
    rewards: dict = Field(default_factory=dict)
    pages: list[LessonBlueprintPage] = Field(default_factory=list)
    story: StoryThread = Field(default_factory=StoryThread)
    teacher_note: str = ""

    def cache_key(self) -> str:
        vocab_key = "|".join(item.key for item in self.target_vocab)
        page_key = "|".join(page.page_type for page in self.pages)
        raw = f"{LESSON_PACKAGE_VERSION}:{self.student_id}:{self.lesson_type}:{self.theme}:{self.level_hint}:{vocab_key}:{page_key}"
        return sha256(raw.encode("utf-8")).hexdigest()


class LessonPackage(BaseModel):
    package_version: str = LESSON_PACKAGE_VERSION
    lesson_id: str
    student_id: str
    pet_id: str = "pet-default"
    title: str
    theme: str = "feed_rabbit"
    estimated_minutes: int = 6
    vocab: list[str]
    target_vocab_items: list[VocabItem] = Field(default_factory=list)
    story: StoryThread = Field(default_factory=StoryThread)
    pages: list[LessonPage] = Field(default_factory=list)
    reward_preview: dict = Field(default_factory=dict)
    focus_tags: list[str] = Field(default_factory=list)
    teacher_note: str = ""
    source_model: str = ""
    debug_metadata: dict = Field(default_factory=dict)


class LessonRequest(BaseModel):
    student_id: str
    requested_vocab: list[str] = Field(default_factory=list)
    lesson_type: str = "pet_feeding"
    level_hint: str = "starter"
    force_regenerate: bool = False

    def cache_key(self) -> str:
        joined = "|".join(sorted(self.requested_vocab))
        raw = f"{self.student_id}:{self.lesson_type}:{self.level_hint}:{joined}:{self.force_regenerate}"
        return sha256(raw.encode("utf-8")).hexdigest()


class LessonResponse(BaseModel):
    lesson: LessonPackage
    source: Literal["generated", "cache"]
    blueprint: LessonBlueprint | None = None
