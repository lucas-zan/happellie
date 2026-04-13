from app.domain.interfaces.analytics import CostTracker
from app.domain.interfaces.pet import PetRepository
from app.schemas.pet import FeedPetRequest, PetFeedResponse, PetSummary, ShopPurchaseRequest, ShopPurchaseResponse


class PetService:
    def __init__(self, pet_repo: PetRepository, cost_tracker: CostTracker) -> None:
        self._pet_repo = pet_repo
        self._cost_tracker = cost_tracker

    def get_pet_summary(self, student_id: str) -> PetSummary:
        return self._pet_repo.get_or_create_pet(student_id)

    def buy_food(self, payload: ShopPurchaseRequest) -> ShopPurchaseResponse:
        prices = {"basic_food": 3, "premium_food": 8, "item_red_scarf": 20, "item_star_hat": 24}
        item_key = payload.food_type
        unit_price = prices.get(item_key, prices["basic_food"])
        qty = max(1, int(payload.quantity or 1))
        cost = unit_price * qty
        pet = self._pet_repo.get_or_create_pet(payload.student_id)
        if pet.coins < cost:
            return ShopPurchaseResponse(status="insufficient_coins", pet=pet, spent_coins=0, purchased_food={})
        pet.coins -= cost
        purchased: dict[str, int] = {}
        if item_key.startswith("item_"):
            for _ in range(qty):
                if item_key not in pet.equipped_items:
                    pet.equipped_items.append(item_key)
            purchased[item_key] = qty
        else:
            pet.food_inventory[item_key] = pet.food_inventory.get(item_key, 0) + qty
            purchased[item_key] = qty
        self._pet_repo.save_pet(pet)
        self._cost_tracker.record(
            "pet_shop_purchase",
            count=qty,
            metadata={"student_id": payload.student_id, "food_type": item_key, "coins": cost},
        )
        return ShopPurchaseResponse(
            status="ok",
            pet=pet,
            spent_coins=cost,
            purchased_food=purchased,
        )

    def feed_pet(self, payload: FeedPetRequest) -> PetFeedResponse:
        pet = self._pet_repo.get_or_create_pet(payload.student_id)
        current = pet.food_inventory.get(payload.food_type, 0)
        if current < payload.quantity:
            return PetFeedResponse(status="insufficient_food", pet=pet, growth_delta={})

        hunger_delta = 10 * payload.quantity
        affection_delta = 3 * payload.quantity
        exp_delta = 12 * payload.quantity
        before_stage = pet.growth_stage
        pet.food_inventory[payload.food_type] = current - payload.quantity
        pet.hunger = min(100, pet.hunger + hunger_delta)
        pet.affection = min(100, pet.affection + affection_delta)
        pet.growth_exp += exp_delta
        while pet.growth_exp >= 100 and pet.growth_stage < 5:
            pet.growth_exp -= 100
            pet.growth_stage += 1
        if pet.hunger >= 85 and pet.affection >= 70:
            pet.emotion_state = "excited"
        elif pet.hunger >= 60:
            pet.emotion_state = "happy"
        else:
            pet.emotion_state = "neutral"
        self._pet_repo.save_pet(pet)
        self._cost_tracker.record("pet_feed", count=payload.quantity, metadata={"student_id": payload.student_id})
        return PetFeedResponse(
            status="ok",
            pet=pet,
            growth_delta={
                "hunger": hunger_delta,
                "affection": affection_delta,
                "growth_exp": exp_delta,
                "growth_stage": max(0, pet.growth_stage - before_stage),
            },
        )
