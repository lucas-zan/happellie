from pydantic import BaseModel, Field


class PetSummary(BaseModel):
    student_id: str
    pet_id: str = "pet-default"
    pet_name: str = "Ellie"
    species: str = "rabbit"
    hunger: int = 50
    weight: int = 50
    affection: int = 50
    growth_stage: int = 1
    coins: int = 0
    food_inventory: dict = Field(default_factory=lambda: {"basic_food": 0})


class FeedPetRequest(BaseModel):
    student_id: str
    food_type: str = "basic_food"
    quantity: int = 1


class PetFeedResponse(BaseModel):
    status: str = "ok"
    pet: PetSummary
    growth_delta: dict = Field(default_factory=dict)
