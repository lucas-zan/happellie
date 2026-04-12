from __future__ import annotations

from typing import Protocol


class StructuredLLMResult(Protocol):
    data: dict
    prompt_tokens: int
    completion_tokens: int
    model: str
    provider: str


class StructuredLLMClient(Protocol):
    def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema_name: str,
        schema: dict,
        model: str,
        temperature: float = 0.3,
    ) -> StructuredLLMResult:
        ...
