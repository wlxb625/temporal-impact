"""FastAPI integration tests for the sidecar endpoints."""

from fastapi.testclient import TestClient

from temporal_impact import ImpactEngine, ShadowNode, ShadowRelation
from temporal_impact.api import create_app


def test_api_accepts_analyzes_and_returns_read_only_outputs(tmp_path: object) -> None:
    """The HTTP workflow uses the same persistent SDK engine."""
    engine = ImpactEngine(database_url=f"sqlite:///{tmp_path / 'api.db'}")
    engine.register_node(
        ShadowNode(
            id="master",
            project_id="project",
            source_system="host",
            source_type="character",
            source_id="master",
        )
    )
    engine.register_node(
        ShadowNode(
            id="chapter",
            project_id="project",
            source_system="host",
            source_type="chapter",
            source_id="1",
        )
    )
    engine.register_relation(
        ShadowRelation(
            id="rel",
            project_id="project",
            source_node_id="master",
            target_node_id="chapter",
            relation_type="conflicts_with",
            weight=1.0,
        )
    )
    client = TestClient(create_app(engine))
    event = {
        "event_id": "api-event",
        "event_type": "object.updated",
        "source": "host",
        "project_id": "project",
        "object": {"type": "character", "id": "master"},
        "before": {"x": 1},
        "after": {"x": 2},
        "occurred_at": "2026-07-15T10:30:00+08:00",
    }
    assert client.get("/health").json() == {"status": "ok"}
    report = client.post("/analyze", json=event).json()
    assert client.get(f"/reports/{report['id']}").status_code == 200
    assert client.get("/projects/project/graph").json()["nodes"]
    proposals = client.get("/projects/project/proposals").json()
    assert client.post(f"/proposals/{proposals[0]['id']}/accept").json()["status"] == "accepted"
