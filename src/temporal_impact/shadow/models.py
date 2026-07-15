"""Shadow graph models that retain references instead of host business data."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

NodeStatus = Literal["valid", "possibly_affected", "conflict", "stale", "discarded", "locked"]
RelationStatus = Literal["valid", "invalid", "discarded"]


class ShadowNode(BaseModel):
    """A compact, version-aware reference to one host-system object."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(min_length=1)
    project_id: str = Field(min_length=1)
    branch_id: str = Field(default="main", min_length=1)
    source_system: str = Field(min_length=1)
    source_type: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    source_revision: str | None = None
    fingerprint: str | None = None
    summary: str | None = None
    importance: float = Field(default=1.0, ge=0.0, le=1.0)
    status: NodeStatus = "valid"


class ShadowRelation(BaseModel):
    """A weighted, explainable directed relation between shadow nodes."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(min_length=1)
    project_id: str = Field(min_length=1)
    branch_id: str = Field(default="main", min_length=1)
    source_node_id: str = Field(min_length=1)
    target_node_id: str = Field(min_length=1)
    relation_type: str = Field(min_length=1)
    weight: float = Field(default=0.5, ge=0.0, le=1.0)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    status: RelationStatus = "valid"
    evidence: dict[str, Any] | None = None
