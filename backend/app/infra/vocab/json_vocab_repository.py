from __future__ import annotations

import json
from pathlib import Path

from app.domain.interfaces.vocab import VocabRepository
from app.schemas.lesson import VocabItem


class JsonFileVocabRepository(VocabRepository):
    def __init__(self, vocab_path: str) -> None:
        self._path = Path(vocab_path)

    def list_vocab(self) -> list[VocabItem]:
        if not self._path.exists():
            return []
        raw = json.loads(self._path.read_text(encoding="utf-8"))
        return [VocabItem.model_validate(item) for item in raw.get("items", [])]

    def get_by_keys(self, keys: list[str]) -> list[VocabItem]:
        wanted = {key.strip() for key in keys if key.strip()}
        if not wanted:
            return []
        matched = [item for item in self.list_vocab() if item.key in wanted or item.text in wanted]
        known = {item.key for item in matched}
        for key in keys:
            normalized = key.strip()
            if normalized and normalized not in known and all(item.text != normalized for item in matched):
                matched.append(
                    VocabItem(
                        key=normalized.lower().replace(" ", "_"),
                        text=normalized,
                        meaning=f"{normalized} 的含义",
                        category="custom",
                        difficulty="starter",
                    )
                )
        return matched
