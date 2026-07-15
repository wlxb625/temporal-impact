"""Pydantic models for the versioned host change-event protocol."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

EventType = Literal[
    "object.created",
    "object.updated",
    "object.deleted",
    "relation.changed",
    "task.completed",
]


class ObjectRef(BaseModel):
    """Reference a host object without copying its business content."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    type: str = Field(min_length=1)
    id: str = Field(min_length=1)
    revision: str | None = None


class ChangeEvent(BaseModel):
    """A validated, traceable change emitted by a host application."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    event_id: str = Field(min_length=1)
    event_type: EventType
    source: str = Field(min_length=1)
    project_id: str = Field(min_length=1)
    branch_id: str = Field(default="main", min_length=1)
    object: ObjectRef
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    occurred_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("occurred_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        """Reject events with ambiguous, timezone-naive occurrence times."""
        if value.tzinfo is None or value.utcoffset() is None:
            msg = "occurred_at must include timezone information"
            raise ValueError(msg)
        return value

    def to_json(self) -> str:
        """Serialize the event to the standard JSON representation."""
        return self.model_dump_json(exclude_none=True)

    @classmethod
    def from_json(cls, payload: str | bytes) -> "ChangeEvent":
        """Parse and validate an event from a JSON string or UTF-8 bytes."""
        return cls.model_validate_json(payload)
