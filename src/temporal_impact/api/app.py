"""FastAPI sidecar exposing the same read-only SDK workflow."""

from fastapi import FastAPI, HTTPException

from temporal_impact.engine import ImpactEngine
from temporal_impact.events import ChangeEvent


def create_app(engine: ImpactEngine | None = None) -> FastAPI:
    """Build a sidecar app with a supplied engine, useful for isolated tests."""
    app = FastAPI(title="Temporal Impact", version="0.1.0-alpha")
    impact_engine = engine or ImpactEngine()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/events", status_code=202)
    def ingest(event: ChangeEvent) -> dict[str, object]:
        return {"event_id": event.event_id, "accepted": impact_engine.ingest(event)}

    @app.post("/analyze")
    def analyze(event: ChangeEvent) -> dict[str, object]:
        return impact_engine.analyze(event).model_dump(mode="json")

    @app.get("/reports/{report_id}")
    def report(report_id: str) -> dict[str, object]:
        result = impact_engine.get_report(report_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Impact report was not found")
        return result.model_dump(mode="json")

    @app.get("/projects/{project_id}/graph")
    def graph(project_id: str, branch_id: str = "main") -> dict[str, object]:
        return impact_engine.graph_data(project_id, branch_id)

    @app.get("/projects/{project_id}/proposals")
    def proposals(project_id: str, branch_id: str = "main") -> list[dict[str, object]]:
        items = impact_engine.list_proposals(project_id, branch_id)
        return [item.model_dump(mode="json") for item in items]

    @app.post("/proposals/{proposal_id}/accept")
    def accept_proposal(proposal_id: str) -> dict[str, object]:
        proposal = impact_engine.repository.update_proposal_status(proposal_id, "accepted")
        if proposal is None:
            raise HTTPException(status_code=404, detail="Proposal was not found")
        return proposal.model_dump(mode="json")

    return app


app = create_app()
