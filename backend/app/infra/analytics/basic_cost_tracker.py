from __future__ import annotations

import json
from collections import defaultdict

from app.domain.interfaces.analytics import CostTracker
from app.infra.db.connection import SqliteConnectionFactory


class SqliteCostTracker(CostTracker):
    def __init__(self, connection_factory: SqliteConnectionFactory) -> None:
        self._connection_factory = connection_factory

    def record(self, category: str, count: int = 1, cost_cents: int = 0, metadata: dict | None = None) -> None:
        with self._connection_factory.connect() as conn:
            conn.execute(
                "INSERT INTO cost_events (category, count, cost_cents, metadata_json) VALUES (?, ?, ?, ?)",
                (category, count, cost_cents, json.dumps(metadata or {}, ensure_ascii=False)),
            )

    def summarize(self) -> dict:
        with self._connection_factory.connect() as conn:
            rows = conn.execute(
                "SELECT category, count, cost_cents, metadata_json FROM cost_events ORDER BY id DESC"
            ).fetchall()
        by_category: dict[str, dict[str, int]] = defaultdict(lambda: {"count": 0, "cost_cents": 0})
        by_provider: dict[str, dict[str, int]] = defaultdict(lambda: {"count": 0, "cost_cents": 0})
        for row in rows:
            metadata = json.loads(row["metadata_json"] or "{}")
            category = row["category"]
            count = int(row["count"] or 0)
            cost_cents = int(row["cost_cents"] or 0)
            by_category[category]["count"] += count
            by_category[category]["cost_cents"] += cost_cents
            provider = str(metadata.get("provider") or "local")
            by_provider[provider]["count"] += count
            by_provider[provider]["cost_cents"] += cost_cents
        total = sum(item["cost_cents"] for item in by_category.values())
        return {
            **by_category,
            "total_cost_cents": total,
            "features": [
                {"feature": key, "count": value["count"], "cost_cents": value["cost_cents"]}
                for key, value in sorted(by_category.items())
            ],
            "ai_usage": [
                {"provider": key, "count": value["count"], "cost_cents": value["cost_cents"]}
                for key, value in sorted(by_provider.items())
            ],
        }
