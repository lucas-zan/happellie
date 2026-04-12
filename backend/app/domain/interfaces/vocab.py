from __future__ import annotations

from typing import Protocol

from app.schemas.lesson import VocabItem


class VocabRepository(Protocol):
    def list_vocab(self) -> list[VocabItem]:
        ...

    def get_by_keys(self, keys: list[str]) -> list[VocabItem]:
        ...
