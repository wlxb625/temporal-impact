"""Typer commands available in the current development stage."""

import json
import subprocess
import sys
from pathlib import Path

import typer
from pydantic import ValidationError

from temporal_impact.config import Settings
from temporal_impact.engine import ImpactEngine
from temporal_impact.events import ChangeEvent

app = typer.Typer(
    add_completion=False,
    help="Validate Temporal Impact change-event JSON files.",
    no_args_is_help=True,
)


@app.callback()
def main() -> None:
    """Run Temporal Impact command-line tools."""


def load_event(event_file: Path) -> ChangeEvent:
    """Read and validate event JSON with a concise user-facing error."""
    try:
        return ChangeEvent.from_json(event_file.read_text(encoding="utf-8"))
    except OSError as error:
        typer.echo(f"Unable to read event file: {error}", err=True)
        raise typer.Exit(code=1) from None
    except ValidationError as error:
        typer.echo(f"Invalid change event: {error}", err=True)
        raise typer.Exit(code=1) from None


@app.command()
def init(database_url: str | None = None) -> None:
    """Initialize the local SQLite database; running this command is safe repeatedly."""
    engine = ImpactEngine(database_url=database_url)
    typer.echo(f"Temporal Impact database is ready: {engine.repository._engine.url}")


@app.command()
def ingest(event_file: Path, database_url: str | None = None) -> None:
    """Validate and locally store one host change event from EVENT_FILE."""
    event = load_event(event_file)
    accepted = ImpactEngine(database_url=database_url).ingest(event)
    outcome = "accepted" if accepted else "already accepted"
    typer.echo(f"Event {outcome}: {event.event_id} ({event.event_type})")


@app.command()
def analyze(event_file: Path, database_url: str | None = None) -> None:
    """Analyze a host event and print its explainable impact report as JSON."""
    report = ImpactEngine(database_url=database_url).analyze(load_event(event_file))
    typer.echo(report.model_dump_json(indent=2))


@app.command()
def graph(project_id: str, branch_id: str = "main", database_url: str | None = None) -> None:
    """Display the compact shadow graph for one project branch."""
    data = ImpactEngine(database_url=database_url).graph_data(project_id, branch_id)
    typer.echo(json.dumps(data, indent=2))


@app.command()
def proposals(project_id: str, branch_id: str = "main", database_url: str | None = None) -> None:
    """Display read-only proposals for a project branch."""
    items = ImpactEngine(database_url=database_url).list_proposals(project_id, branch_id)
    typer.echo(json.dumps([item.model_dump(mode="json") for item in items], indent=2))


@app.command()
def serve(host: str | None = None, port: int | None = None) -> None:
    """Run the local FastAPI sidecar service."""
    import uvicorn

    settings = Settings()
    uvicorn.run(
        "temporal_impact.api.app:app",
        host=host or settings.host,
        port=port or settings.port,
    )


@app.command()
def demo() -> None:
    """Launch the local Streamlit demonstration without external services."""
    demo_path = Path(__file__).resolve().parents[1] / "demo" / "app.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(demo_path)], check=False)
