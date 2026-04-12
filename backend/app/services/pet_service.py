from app.domain.interfaces.analytics import CostTracker
from app.domain.interfaces.pet import PetRepository
from app.schemas.pet import FeedPetRequest, PetFeedResponse, PetSummary


class PetService:
    def __init__(self, pet_repo: PetRepository, cost_tracker: CostTracker) -> None:
        self._pet_repo = pet_repo
        self._cost_tracker = cost_tracker

    def get_pet_summary(self, student_id: str) -> PetSummary:
        return self._pet_repo.get_or_create_pet(student_id)

    def feed_pet(self, payload: FeedPetRequest) -> PetFeedResponse:
        pet = self._pet_repo.get_or_create_pet(payload.student_id)
        current = pet.food_inventory.get(payload.food_type, 0)
        if current < payload.quantity:
            return PetFeedResponse(status="insufficient_food", pet=pet, growth_delta={})

        pet.food_inventory[payload.food_type] = current - payload.quantity
        pet.hunger = min(100, pet.hunger + 10 * payload.quantity)
        pet.affection = min(100, pet.affection + 3 * payload.quantity)
        if pet.hunger > 80 and pet.growth_stage < 5:
            pet.growth_stage += 1
        self._pet_repo.save_pet(pet)
        self._cost_tracker.record("pet_feed", count=payload.quantity, metadata={"student_id": payload.student_id})
        return PetFeedResponse(
            status="ok",
            pet=pet,
            growth_delta={"hunger": 10 * payload.quantity, "affection": 3 * payload.quantity},
        )
