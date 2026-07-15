"""Explainable impact report models."""

from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

ImpactLevel = Literal["conflict", "high", "medium", "low"]


class PathEdge(BaseModel):
    """One documented edge in an impact propagation path."""

    relation_id: str
    relation_type: str
    weight: float
    confidence: float
    source_node_id: str
    target_node_id: str


class ImpactResult(BaseModel):
    """One affected target with score, level, path, and human-readable reason."""

    target_node_id: str
    score: float = Field(ge=0.0, le=1.0)
    level: ImpactLevel
    distance: int = Field(ge=1)
    path: list[PathEdge]
    reason: str


class ImpactReport(BaseModel):
    """Traceable output of analyzing a single change event."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: str(uuid4()))
    source_event_id: str
    project_id: str
    branch_id: str
    source_node_ids: list[str] = Field(default_factory=list)
    impacts: list[ImpactResult] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
