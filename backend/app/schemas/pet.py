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
    growth_exp: int = 0
    emotion_state: str = "neutral"
    coins: int = 0
    food_inventory: dict = Field(default_factory=lambda: {"basic_food": 0})
    equipped_items: list[str] = Field(default_factory=list)


class FeedPetRequest(BaseModel):
    student_id: str
    food_type: str = "basic_food"
    quantity: int = 1


class ShopPurchaseRequest(BaseModel):
    student_id: str
    food_type: str = "basic_food"
    quantity: int = 1


class PetFeedResponse(BaseModel):
    status: str = "ok"
    pet: PetSummary
    growth_delta: dict = Field(default_factory=dict)


class ShopPurchaseResponse(BaseModel):
    status: str = "ok"
    pet: PetSummary
    spent_coins: int = 0
    purchased_food: dict = Field(default_factory=dict)
