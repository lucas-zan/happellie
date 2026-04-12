import json

from app.domain.interfaces.pet import PetRepository
from app.infra.db.connection import SqliteConnectionFactory
from app.schemas.pet import PetSummary


class SqlitePetRepository(PetRepository):
    def __init__(self, connection_factory: SqliteConnectionFactory) -> None:
        self._connection_factory = connection_factory

    def get_or_create_pet(self, student_id: str) -> PetSummary:
        with self._connection_factory.connect() as conn:
            row = conn.execute("SELECT pet_json FROM pets WHERE student_id = ?", (student_id,)).fetchone()
            if row:
                return PetSummary.model_validate(json.loads(row["pet_json"]))
            pet = PetSummary(student_id=student_id)
            conn.execute(
                "INSERT INTO pets (student_id, pet_json) VALUES (?, ?)",
                (student_id, pet.model_dump_json()),
            )
            return pet

    def save_pet(self, pet: PetSummary) -> None:
        with self._connection_factory.connect() as conn:
            conn.execute(
                "REPLACE INTO pets (student_id, pet_json, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                (pet.student_id, pet.model_dump_json()),
            )
