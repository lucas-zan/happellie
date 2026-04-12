from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass
class StructuredResponse:
    data: dict
    prompt_tokens: int
    completion_tokens: int
    model: str
    provider: str


class OpenAICompatibleStructuredLLM:
    def __init__(
        self,
        *,
        provider_name: str,
        api_key: str,
        base_url: str,
        timeout_seconds: int = 30,
        extra_headers: dict | None = None,
    ) -> None:
        self._provider_name = provider_name
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._extra_headers = extra_headers or {}

    @property
    def enabled(self) -> bool:
        return bool(self._api_key and self._base_url)

    def generate_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema_name: str,
        schema: dict,
        model: str,
        temperature: float = 0.3,
    ) -> StructuredResponse:
        if not self.enabled:
            raise RuntimeError("Structured LLM client is not configured")
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": schema_name, "schema": schema},
            },
        }
        data = self._post("/chat/completions", payload)
        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        content = message.get("content")
        parsed = self._extract_json(content)
        usage = data.get("usage") or {}
        return StructuredResponse(
            data=parsed,
            prompt_tokens=int(usage.get("prompt_tokens") or 0),
            completion_tokens=int(usage.get("completion_tokens") or 0),
            model=data.get("model") or model,
            provider=self._provider_name,
        )

    def _post(self, path: str, payload: dict) -> dict:
        request = urllib.request.Request(
            url=f"{self._base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._api_key}",
                **self._extra_headers,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"LLM HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"LLM request failed: {exc}") from exc

    def _extract_json(self, content: object) -> dict:
        if isinstance(content, str):
            return json.loads(content)
        if isinstance(content, list):
            text_parts: list[str] = []
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        text_parts.append(str(item.get("text") or ""))
                    elif "text" in item:
                        text_parts.append(str(item.get("text") or ""))
            return json.loads("".join(text_parts))
        raise RuntimeError("LLM response did not contain JSON text")
