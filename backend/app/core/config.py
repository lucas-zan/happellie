from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "dev"
    app_port: int = 8000
    database_url: str = "sqlite:///./data/happyellie.db"
    asset_dir: str = "./data/assets"
    frontend_api_base: str = "http://127.0.0.1:8000/api/v1"

    # Vocab and curriculum
    vocab_library_path: str = "./config/vocab_library.json"
    profile_recent_sessions_limit: int = 8
    planner_candidate_limit: int = 14
    default_student_id: str = "student-demo"

    # AI provider: generic OpenAI-compatible configuration.
    ai_provider_name: str = "compatible"
    ai_enable_fallback: bool = True
    ai_timeout_seconds: int = 30
    ai_temperature: float = 0.3
    ai_api_key: str = ""
    ai_base_url: str = ""
    ai_default_model: str = ""
    ai_planner_model: str = ""
    ai_generator_model: str = ""
    ai_profile_model: str = ""
    ai_input_cost_per_million: float = 0.0
    ai_output_cost_per_million: float = 0.0
    ai_headers_json: str = "{}"

    # Backward-compatible aliases for the previous Qwen-only setup.
    qwen_api_key: str = ""
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_model: str = "qwen-flash"
    qwen_timeout_seconds: int = 20

    # TTS can stay disabled during the AI-first prototype stage.
    tts_provider: str = "disabled"

    @property
    def database_path(self) -> str:
        return self.database_url.replace("sqlite:///", "")

    @property
    def asset_path(self) -> Path:
        return Path(self.asset_dir)

    @property
    def vocab_library_file(self) -> Path:
        return Path(self.vocab_library_path)

    @property
    def compatible_api_key(self) -> str:
        return self.ai_api_key or self.qwen_api_key

    @property
    def compatible_base_url(self) -> str:
        return (self.ai_base_url or self.qwen_base_url).rstrip("/")

    @property
    def compatible_default_model(self) -> str:
        return self.ai_default_model or self.qwen_model

    @property
    def compatible_planner_model(self) -> str:
        return self.ai_planner_model or self.compatible_default_model

    @property
    def compatible_generator_model(self) -> str:
        return self.ai_generator_model or self.compatible_default_model

    @property
    def compatible_profile_model(self) -> str:
        return self.ai_profile_model or self.compatible_default_model

    @property
    def compatible_timeout_seconds(self) -> int:
        return self.ai_timeout_seconds or self.qwen_timeout_seconds


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
