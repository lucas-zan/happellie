from typing import Protocol

from app.schemas.pet import PetSummary


class PetRepository(Protocol):
    def get_or_create_pet(self, student_id: str) -> PetSummary:
        ...

    def save_pet(self, pet: PetSummary) -> None:
        ...
