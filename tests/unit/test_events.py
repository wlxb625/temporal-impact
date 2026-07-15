"""Unit tests for the standard change-event protocol."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from temporal_impact import ChangeEvent, ObjectRef
from temporal_impact.events import InMemoryEventRegistry


def event_data() -> dict[str, object]:
    """Return a complete, valid event payload for protocol tests."""
    return {
        "event_id": "evt-001",
        "event_type": "object.updated",
        "source": "example-app",
        "project_id": "project-001",
        "branch_id": "main",
        "object": {"type": "character", "id": "master", "revision": "8"},
        "before": {"real_status": "dead"},
        "after": {"real_status": "hidden_alive"},
        "occurred_at": "2026-07-15T10:30:00+08:00",
        "metadata": {"reason": "setting change"},
    }


def test_event_round_trips_through_json() -> None:
    """The canonical JSON form can be validated back into the same event."""
    event = ChangeEvent.model_validate(event_data())

    restored_event = ChangeEvent.from_json(event.to_json())

    assert restored_event == event


@pytest.mark.parametrize(
    "event_type",
    [
        "object.created",
        "object.updated",
        "object.deleted",
        "relation.changed",
        "task.completed",
    ],
)
def test_all_supported_event_types_are_accepted(event_type: str) -> None:
    """v0.1 accepts exactly the five documented change categories."""
    payload = event_data()
    payload["event_type"] = event_type

    assert ChangeEvent.model_validate(payload).event_type == event_type


def test_unknown_event_type_is_rejected() -> None:
    """Unsupported event categories cannot enter the engine."""
    payload = event_data()
    payload["event_type"] = "object.renamed"

    with pytest.raises(ValidationError, match="event_type"):
        ChangeEvent.model_validate(payload)


def test_event_requires_timezone_aware_time() -> None:
    """Naive datetimes are rejected to preserve event ordering semantics."""
    payload = event_data()
    payload["occurred_at"] = datetime(2026, 7, 15, 10, 30)

    with pytest.raises(ValidationError, match="timezone"):
        ChangeEvent.model_validate(payload)


def test_object_reference_rejects_empty_identity() -> None:
    """Object references must always identify a host object."""
    with pytest.raises(ValidationError):
        ObjectRef(type="character", id=" ")


def test_repeated_event_id_is_idempotent() -> None:
    """The registry returns the original event instead of accepting a duplicate."""
    registry = InMemoryEventRegistry()
    original_event = ChangeEvent.model_validate(event_data())
    duplicate_payload = event_data()
    duplicate_payload["after"] = {"real_status": "unknown"}
    duplicate_event = ChangeEvent.model_validate(duplicate_payload)

    first_result = registry.ingest(original_event)
    duplicate_result = registry.ingest(duplicate_event)

    assert not first_result.is_duplicate
    assert duplicate_result.is_duplicate
    assert duplicate_result.event == original_event
    assert registry.get(original_event.event_id) == original_event


def test_timezone_aware_datetime_is_accepted() -> None:
    """Programmatic callers can pass aware datetime objects directly."""
    payload = event_data()
    payload["occurred_at"] = datetime(2026, 7, 15, 10, 30, tzinfo=UTC)

    assert ChangeEvent.model_validate(payload).occurred_at.tzinfo is UTC
