from app.domain.interfaces.tts import TextToSpeechProvider


class DisabledTextToSpeechProvider(TextToSpeechProvider):
    def synthesize(self, text: str, voice: str = "default") -> str:
        return ""
