from pydantic import BaseModel, Field


class MetricCard(BaseModel):
    key: str
    label: str
    value: int | float | str
    unit: str = ""


class AdminOverviewResponse(BaseModel):
    summary: list[MetricCard] = Field(default_factory=list)
    feature_costs: list[dict] = Field(default_factory=list)
    ai_usage: list[dict] = Field(default_factory=list)
    students: list[dict] = Field(default_factory=list)
