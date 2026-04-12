from __future__ import annotations

import json
from functools import lru_cache

from app.core.config import get_settings
from app.domain.interfaces.analytics import CostTracker, ProfileAnalyzer
from app.domain.interfaces.lesson import ContentRepository, LessonGenerator
from app.domain.interfaces.llm import StructuredLLMClient
from app.domain.interfaces.pet import PetRepository
from app.domain.interfaces.planning import LessonPlanner
from app.domain.interfaces.session import SessionRepository, UsageStatsRepository
from app.domain.interfaces.tts import TextToSpeechProvider
from app.domain.interfaces.vocab import VocabRepository
from app.infra.ai.ai_lesson_generator import AILessonGenerator
from app.infra.ai.openai_compatible_structured_llm import OpenAICompatibleStructuredLLM
from app.infra.ai.rules_lesson_generator import RulesLessonGenerator
from app.infra.analytics.ai_profile_analyzer import AIProfileAnalyzer
from app.infra.analytics.basic_cost_tracker import SqliteCostTracker
from app.infra.analytics.rules_profile_analyzer import RulesProfileAnalyzer
from app.infra.db.connection import SqliteConnectionFactory
from app.infra.planning.ai_lesson_planner import AILessonPlanner
from app.infra.planning.rules_lesson_planner import RulesLessonPlanner
from app.infra.repositories.sqlite_content_repository import SqliteContentRepository
from app.infra.repositories.sqlite_pet_repository import SqlitePetRepository
from app.infra.repositories.sqlite_session_repository import SqliteSessionRepository
from app.infra.tts.disabled_tts_provider import DisabledTextToSpeechProvider
from app.infra.tts.mock_tts_provider import MockTextToSpeechProvider
from app.infra.vocab.json_vocab_repository import JsonFileVocabRepository
from app.services.admin_service import AdminService
from app.services.lesson_service import LessonService
from app.services.pet_service import PetService
from app.services.profile_service import ProfileService
from app.services.session_service import SessionService


@lru_cache(maxsize=1)
def get_connection_factory() -> SqliteConnectionFactory:
    return SqliteConnectionFactory(get_settings().database_path)


@lru_cache(maxsize=1)
def get_content_repository() -> ContentRepository:
    return SqliteContentRepository(get_connection_factory())


@lru_cache(maxsize=1)
def get_session_repository() -> SessionRepository:
    return SqliteSessionRepository(get_connection_factory())


@lru_cache(maxsize=1)
def get_usage_stats_repository() -> UsageStatsRepository:
    return SqliteSessionRepository(get_connection_factory())


@lru_cache(maxsize=1)
def get_pet_repository() -> PetRepository:
    return SqlitePetRepository(get_connection_factory())


@lru_cache(maxsize=1)
def get_vocab_repository() -> VocabRepository:
    return JsonFileVocabRepository(get_settings().vocab_library_path)


@lru_cache(maxsize=1)
def get_cost_tracker() -> CostTracker:
    return SqliteCostTracker(get_connection_factory())


@lru_cache(maxsize=1)
def get_structured_llm() -> StructuredLLMClient:
    settings = get_settings()
    try:
        extra_headers = json.loads(settings.ai_headers_json or "{}")
    except json.JSONDecodeError:
        extra_headers = {}
    return OpenAICompatibleStructuredLLM(
        provider_name=settings.ai_provider_name,
        api_key=settings.compatible_api_key,
        base_url=settings.compatible_base_url,
        timeout_seconds=settings.compatible_timeout_seconds,
        extra_headers=extra_headers,
    )


@lru_cache(maxsize=1)
def get_fallback_lesson_planner() -> LessonPlanner:
    return RulesLessonPlanner()


@lru_cache(maxsize=1)
def get_lesson_planner() -> LessonPlanner:
    settings = get_settings()
    llm = get_structured_llm()
    if not getattr(llm, "enabled", False):
        return get_fallback_lesson_planner()
    return AILessonPlanner(
        llm=llm,
        model=settings.compatible_planner_model,
        cost_tracker=get_cost_tracker(),
        provider_name=settings.ai_provider_name,
        input_cost_per_million=settings.ai_input_cost_per_million,
        output_cost_per_million=settings.ai_output_cost_per_million,
        temperature=settings.ai_temperature,
    )


@lru_cache(maxsize=1)
def get_fallback_lesson_generator() -> LessonGenerator:
    return RulesLessonGenerator()


@lru_cache(maxsize=1)
def get_ai_lesson_generator() -> LessonGenerator:
    settings = get_settings()
    llm = get_structured_llm()
    if not getattr(llm, "enabled", False):
        return get_fallback_lesson_generator()
    return AILessonGenerator(
        llm=llm,
        model=settings.compatible_generator_model,
        cost_tracker=get_cost_tracker(),
        provider_name=settings.ai_provider_name,
        input_cost_per_million=settings.ai_input_cost_per_million,
        output_cost_per_million=settings.ai_output_cost_per_million,
        temperature=settings.ai_temperature,
    )


@lru_cache(maxsize=1)
def get_tts_provider() -> TextToSpeechProvider:
    settings = get_settings()
    if settings.tts_provider == "mock":
        return MockTextToSpeechProvider()
    return DisabledTextToSpeechProvider()


@lru_cache(maxsize=1)
def get_fallback_profile_analyzer() -> ProfileAnalyzer:
    return RulesProfileAnalyzer()


@lru_cache(maxsize=1)
def get_ai_profile_analyzer() -> ProfileAnalyzer:
    settings = get_settings()
    llm = get_structured_llm()
    if not getattr(llm, "enabled", False):
        return get_fallback_profile_analyzer()
    return AIProfileAnalyzer(
        llm=llm,
        model=settings.compatible_profile_model,
        cost_tracker=get_cost_tracker(),
        provider_name=settings.ai_provider_name,
        input_cost_per_million=settings.ai_input_cost_per_million,
        output_cost_per_million=settings.ai_output_cost_per_million,
        temperature=max(0.1, settings.ai_temperature - 0.05),
    )


@lru_cache(maxsize=1)
def get_lesson_service() -> LessonService:
    settings = get_settings()
    return LessonService(
        content_repo=get_content_repository(),
        session_repo=get_session_repository(),
        vocab_repo=get_vocab_repository(),
        lesson_planner=get_lesson_planner(),
        fallback_lesson_planner=get_fallback_lesson_planner(),
        ai_lesson_generator=get_ai_lesson_generator(),
        fallback_lesson_generator=get_fallback_lesson_generator(),
        tts_provider=get_tts_provider(),
        cost_tracker=get_cost_tracker(),
        enable_fallback=settings.ai_enable_fallback,
    )


@lru_cache(maxsize=1)
def get_session_service() -> SessionService:
    settings = get_settings()
    return SessionService(
        session_repo=get_session_repository(),
        pet_repo=get_pet_repository(),
        ai_profile_analyzer=get_ai_profile_analyzer(),
        fallback_profile_analyzer=get_fallback_profile_analyzer(),
        cost_tracker=get_cost_tracker(),
        recent_sessions_limit=settings.profile_recent_sessions_limit,
        enable_fallback=settings.ai_enable_fallback,
    )


@lru_cache(maxsize=1)
def get_pet_service() -> PetService:
    return PetService(
        pet_repo=get_pet_repository(),
        cost_tracker=get_cost_tracker(),
    )


@lru_cache(maxsize=1)
def get_admin_service() -> AdminService:
    return AdminService(
        usage_repo=get_usage_stats_repository(),
        cost_tracker=get_cost_tracker(),
        pet_repo=get_pet_repository(),
    )


@lru_cache(maxsize=1)
def get_profile_service() -> ProfileService:
    return ProfileService(get_session_repository())
