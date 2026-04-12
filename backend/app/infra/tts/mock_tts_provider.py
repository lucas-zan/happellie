from __future__ import annotations

from hashlib import sha1
from pathlib import Path

from app.core.config import get_settings
from app.domain.interfaces.tts import TextToSpeechProvider


class MockTextToSpeechProvider(TextToSpeechProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self._audio_dir = settings.asset_path / "audio"
        self._audio_dir.mkdir(parents=True, exist_ok=True)

    def synthesize(self, text: str, voice: str = "default") -> str:
        digest = sha1((voice + ":" + text).encode("utf-8")).hexdigest()
        audio_path = self._audio_dir / f"{digest}.txt"
        if not audio_path.exists():
            audio_path.write_text(f"MOCK AUDIO\nvoice={voice}\ntext={text}\n", encoding="utf-8")
        return f"/assets/audio/{audio_path.name}"
