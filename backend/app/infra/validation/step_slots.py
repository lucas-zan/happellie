from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class CharacterRef(BaseModel):
    id: str = "ellie"
    mood: str = "happy"
    line: str = ""


class DialogueLine(BaseModel):
    character: str = "narrator"
    mood: str = "neutral"
    line: str


class StoryDialogueSlots(BaseModel):
    background: str = "default"
    dialogues: list[DialogueLine] = Field(default_factory=list)


class StoryChoiceOption(BaseModel):
    key: str
    text: str
    consequence_tag: str = "neutral"


class StoryChoiceSlots(BaseModel):
    character: CharacterRef = Field(default_factory=CharacterRef)
    scenario: str = ""
    choices: list[StoryChoiceOption] = Field(default_factory=list)


class MissionBriefingSlots(BaseModel):
    companion: CharacterRef = Field(default_factory=CharacterRef)
    objectives: list[str] = Field(default_factory=list)


class WordRevealSlots(BaseModel):
    word: str
    meaning: str
    image_hint: str = ""
    audio_text: str = ""
    sentence: str = ""
    character: CharacterRef = Field(default_factory=CharacterRef)


class WordInSceneWord(BaseModel):
    word: str
    meaning: str = ""
    position_hint: str = ""


class WordInSceneSlots(BaseModel):
    scene_hint: str = "default"
    hidden_words: list[WordInSceneWord] = Field(default_factory=list)


class ListenPickOption(BaseModel):
    key: str
    image_hint: str = ""


class ListenPickSlots(BaseModel):
    character: CharacterRef = Field(default_factory=CharacterRef)
    audio_text: str
    options: list[ListenPickOption] = Field(default_factory=list)
    correct_key: str
    success_line: str = "Great job!"
    fail_line: str = "Not quite. Try again!"


class DragMatchPair(BaseModel):
    left: str
    right: str


class DragMatchSlots(BaseModel):
    character: CharacterRef = Field(default_factory=CharacterRef)
    pairs: list[DragMatchPair] = Field(default_factory=list)
    match_type: Literal["text_to_text", "text_to_image"] = "text_to_text"


class ChoiceBattleRound(BaseModel):
    question: str
    options: list[str] = Field(default_factory=list)
    answer: str
    round_type: Literal["text", "image", "audio"] = "text"


class ChoiceBattleMonster(BaseModel):
    id: str = "snack_thief"
    name: str = "Snack Thief"
    hp: int = 3


class ChoiceBattleSlots(BaseModel):
    monster: ChoiceBattleMonster = Field(default_factory=ChoiceBattleMonster)
    companion: CharacterRef = Field(default_factory=CharacterRef)
    rounds: list[ChoiceBattleRound] = Field(default_factory=list)
    victory_line: str = "You win!"
    defeat_line: str = "Try again next time!"


class SentencePuzzleSlots(BaseModel):
    character: CharacterRef = Field(default_factory=CharacterRef)
    target_sentence: str
    scrambled_words: list[str] = Field(default_factory=list)
    hint: str = ""


class SpeakRepeatSlots(BaseModel):
    character: CharacterRef = Field(default_factory=CharacterRef)
    audio_text: str
    display_text: str = ""


class RewardChestSlots(BaseModel):
    total_coins: int = 0
    total_food: dict = Field(default_factory=dict)
    bonus_item: dict | None = None


class FeedPetStepSlots(BaseModel):
    available_food: dict = Field(default_factory=dict)
    pet_current_mood: str = "hungry"


class EpisodeEndSlots(BaseModel):
    episode_summary: str = ""
    next_hook: str = ""
    next_episode_hint: str = ""
    companion_farewell: CharacterRef = Field(default_factory=CharacterRef)

