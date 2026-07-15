"""In-memory event ingestion with event-id idempotence."""

from dataclasses import dataclass

from temporal_impact.events.models import ChangeEvent


@dataclass(frozen=True, slots=True)
class EventIngestResult:
    """The outcome of accepting an event into the current process."""

    event: ChangeEvent
    is_duplicate: bool


class InMemoryEventRegistry:
    """Accept each event identifier at most once during the process lifetime."""

    def __init__(self) -> None:
        self._events: dict[str, ChangeEvent] = {}

    def ingest(self, event: ChangeEvent) -> EventIngestResult:
        """Register an event or return its original instance when it is repeated."""
        existing_event = self._events.get(event.event_id)
        if existing_event is not None:
            return EventIngestResult(event=existing_event, is_duplicate=True)

        self._events[event.event_id] = event
        return EventIngestResult(event=event, is_duplicate=False)

    def get(self, event_id: str) -> ChangeEvent | None:
        """Return a previously accepted event by identifier, if present."""
        return self._events.get(event_id)
