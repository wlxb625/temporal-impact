"""Integration tests for the event-validation CLI command."""

import json
from pathlib import Path

from typer.testing import CliRunner

from temporal_impact.cli.app import app

runner = CliRunner()


def valid_event() -> dict[str, object]:
    """Return a valid event payload for CLI tests."""
    return {
        "event_id": "evt-cli-001",
        "event_type": "object.updated",
        "source": "example-app",
        "project_id": "project-001",
        "object": {"type": "character", "id": "master"},
        "occurred_at": "2026-07-15T10:30:00+08:00",
    }


def test_ingest_validates_a_json_file(tmp_path: Path) -> None:
    """The command confirms a valid event without exposing internals."""
    event_file = tmp_path / "event.json"
    event_file.write_text(json.dumps(valid_event()), encoding="utf-8")

    database_url = f"sqlite:///{tmp_path / 'impact.db'}"
    result = runner.invoke(app, ["ingest", str(event_file), "--database-url", database_url])

    assert result.exit_code == 0
    assert "Event accepted: evt-cli-001 (object.updated)" in result.output


def test_ingest_reports_invalid_events_cleanly(tmp_path: Path) -> None:
    """Malformed protocol data produces a concise command failure."""
    event_file = tmp_path / "event.json"
    invalid_event = valid_event()
    invalid_event["occurred_at"] = "2026-07-15T10:30:00"
    event_file.write_text(json.dumps(invalid_event), encoding="utf-8")

    database_url = f"sqlite:///{tmp_path / 'impact.db'}"
    result = runner.invoke(app, ["ingest", str(event_file), "--database-url", database_url])

    assert result.exit_code == 1
    assert "Invalid change event" in result.output
