from __future__ import annotations

from pydantic import BaseModel, Field


class SessionSignals(BaseModel):
    duration_seconds: int = 0
    correct_count: int = 0
    wrong_count: int = 0
    speaking_attempts: int = 0
    preferred_block_types: list[str] = Field(default_factory=list)
    completed_blocks: int = 0
    total_blocks: int = 0
    score: int = 0
    earned_food: int = 0
    earned_coins: int = 0
    story_arc_key: str = "snack_scouts"
    story_episode_index: int = 1
    story_last_scene: str = ""
    story_next_hook: str = ""
    encountered_characters: list[str] = Field(default_factory=list)


class RecentSessionSummary(BaseModel):
    lesson_id: str
    duration_seconds: int
    total_score: int
    earned_food: int = 0
    earned_coins: int = 0
    wrong_count: int = 0
    preferred_block_types: list[str] = Field(default_factory=list)
    created_at: str = ""


class ProfileSnapshot(BaseModel):
    student_id: str
    weak_vocab_tags: list[str] = Field(default_factory=list)
    weak_skill_tags: list[str] = Field(default_factory=list)
    interest_tags: list[str] = Field(default_factory=lambda: ["pet_feeding"])
    preferred_themes: list[str] = Field(default_factory=lambda: ["feed_rabbit"])
    recommended_session_minutes: int = 8
    motivation_level: str = "medium"
    frustration_risk: str = "low"
    current_level: str = "starter"
    latest_focus: list[str] = Field(default_factory=list)
    recommended_vocab_keys: list[str] = Field(default_factory=list)
    summary_note: str = ""
    story_arc_key: str = "snack_scouts"
    story_episode_index: int = 0
    story_last_scene: str = ""
    story_next_hook: str = ""
    story_characters: list[str] = Field(default_factory=list)
    updated_at: str = ""
