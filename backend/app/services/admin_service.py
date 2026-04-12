from app.domain.interfaces.analytics import CostTracker
from app.domain.interfaces.pet import PetRepository
from app.domain.interfaces.session import UsageStatsRepository
from app.schemas.admin import AdminOverviewResponse, MetricCard


class AdminService:
    def __init__(self, usage_repo: UsageStatsRepository, cost_tracker: CostTracker, pet_repo: PetRepository) -> None:
        self._usage_repo = usage_repo
        self._cost_tracker = cost_tracker
        self._pet_repo = pet_repo

    def get_overview(self) -> AdminOverviewResponse:
        usage = self._usage_repo.get_usage_overview()
        costs = self._cost_tracker.summarize()
        ai_calls = sum(
            value.get("count", 0)
            for key, value in costs.items()
            if isinstance(value, dict) and key.startswith("ai_")
        )
        cards = [
            MetricCard(key="sessions", label="Sessions", value=usage.get("sessions", 0)),
            MetricCard(key="usage_minutes", label="Usage Minutes", value=usage.get("usage_minutes", 0), unit="min"),
            MetricCard(key="ai_calls", label="AI Calls", value=ai_calls),
            MetricCard(key="cost_cents", label="Tracked Cost", value=costs.get("total_cost_cents", 0), unit="cents"),
        ]
        return AdminOverviewResponse(
            summary=cards,
            feature_costs=costs.get("features", []),
            ai_usage=costs.get("ai_usage", []),
            students=usage.get("students", []),
        )
