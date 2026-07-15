"""Incremental observation records."""

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field

ObservationKind = Literal["conflict_score", "staleness_score", "stability_score"]


class ObservationValue(BaseModel):
    """One versioned score calculated for a shadow target."""

    id: str
    project_id: str
    branch_id: str
    target_node_id: str
    kind: ObservationKind
    value: float = Field(ge=0.0, le=1.0)
    previous_value: float | None = Field(default=None, ge=0.0, le=1.0)
    status: str = "valid"
    calculation_version: str = "v0.1"
    source_event_id: str
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ObservationDependency(BaseModel):
    """A compact dependency reference used to explain a recalculation."""

    observation_id: str
    node_id: str
    relation_id: str | None = None
