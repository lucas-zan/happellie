from typing import Protocol


class TextToSpeechProvider(Protocol):
    def synthesize(self, text: str, voice: str = "default") -> str:
        """Return a local asset path or URL."""
        ...
