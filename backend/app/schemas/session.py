from __future__ import annotations

from pydantic import BaseModel, Field


class SessionBlockResult(BaseModel):
    block_id: str
    block_type: str
    correct: bool = True
    score: int = 0
    duration_ms: int = 0


class SessionCompleteRequest(BaseModel):
    student_id: str
    lesson_id: str
    duration_seconds: int
    total_score: int
    earned_food: int = 0
    earned_coins: int = 0
    story_arc_key: str = "snack_scouts"
    story_episode_index: int = 1
    story_last_scene: str = ""
    story_next_hook: str = ""
    encountered_characters: list[str] = Field(default_factory=list)
    block_results: list[SessionBlockResult] = Field(default_factory=list)


class SessionCompleteResponse(BaseModel):
    status: str = "ok"
    next_recommendation: dict = Field(default_factory=dict)
    updated_profile: dict = Field(default_factory=dict)
