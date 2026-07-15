"""Read-only proposal models and status transitions."""

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import NAMESPACE_URL, uuid5

from pydantic import BaseModel, Field

ProposalType = Literal[
    "review_required",
    "mark_stale",
    "create_revision_task",
    "branch_recommended",
    "recalculate_required",
]
ProposalStatus = Literal["pending", "accepted", "rejected", "applied", "obsolete"]


class Proposal(BaseModel):
    """A traceable suggestion that never changes a host object by itself."""

    id: str
    project_id: str
    branch_id: str
    source_event_id: str
    target_node_id: str
    proposal_type: ProposalType
    priority: float = Field(ge=0.0, le=1.0)
    reason: str
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    status: ProposalStatus = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def stable_id(cls, event_id: str, target_node_id: str, proposal_type: ProposalType) -> str:
        """Produce a deterministic ID that prevents duplicate recommendations."""
        return str(uuid5(NAMESPACE_URL, f"{event_id}:{target_node_id}:{proposal_type}"))
