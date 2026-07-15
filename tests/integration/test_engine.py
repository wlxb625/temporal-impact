"""Integration tests for the public SDK workflow."""

from pathlib import Path

from temporal_impact import ChangeEvent, ImpactEngine, ShadowNode, ShadowRelation


def test_sdk_persists_reports_observations_and_proposals(tmp_path: Path) -> None:
    """A complete event analysis remains available after engine restart."""
    database_url = f"sqlite:///{tmp_path / 'engine.db'}"
    engine = ImpactEngine(database_url=database_url)
    engine.register_node(
        ShadowNode(
            id="master",
            project_id="novel",
            source_system="novel-app",
            source_type="character",
            source_id="master",
        )
    )
    engine.register_node(
        ShadowNode(
            id="chapter-12",
            project_id="novel",
            source_system="novel-app",
            source_type="chapter",
            source_id="12",
            importance=1.0,
        )
    )
    engine.register_relation(
        ShadowRelation(
            id="master-conflicts-chapter-12",
            project_id="novel",
            source_node_id="master",
            target_node_id="chapter-12",
            relation_type="conflicts_with",
            weight=1.0,
        )
    )
    event = ChangeEvent.model_validate(
        {
            "event_id": "master-alive",
            "event_type": "object.updated",
            "source": "novel-app",
            "project_id": "novel",
            "object": {"type": "character", "id": "master"},
            "before": {"status": "dead"},
            "after": {"status": "hidden_alive"},
            "occurred_at": "2026-07-15T10:30:00+08:00",
        }
    )

    report = engine.analyze(event)
    duplicate_report = engine.analyze(event)
    restarted = ImpactEngine(database_url=database_url)

    assert duplicate_report.id == report.id
    assert restarted.get_report(report.id) == report
    assert report.impacts[0].target_node_id == "chapter-12"
    assert restarted.repository.get_observations("novel")
    proposals = restarted.list_proposals("novel")
    assert {proposal.proposal_type for proposal in proposals} >= {
        "review_required",
        "mark_stale",
        "create_revision_task",
        "branch_recommended",
        "recalculate_required",
    }


def test_new_event_obsoletes_prior_pending_proposals(tmp_path: Path) -> None:
    """A newer source event retires earlier suggestions for the same target."""
    database_url = f"sqlite:///{tmp_path / 'obsolete.db'}"
    engine = ImpactEngine(database_url=database_url)
    engine.register_node(
        ShadowNode(
            id="source",
            project_id="project",
            source_system="host",
            source_type="object",
            source_id="1",
        )
    )
    engine.register_node(
        ShadowNode(
            id="target",
            project_id="project",
            source_system="host",
            source_type="object",
            source_id="2",
        )
    )
    engine.register_relation(
        ShadowRelation(
            id="rel",
            project_id="project",
            source_node_id="source",
            target_node_id="target",
            relation_type="conflicts_with",
            weight=1.0,
        )
    )
    for event_id in ["first", "second"]:
        engine.analyze(
            ChangeEvent.model_validate(
                {
                    "event_id": event_id,
                    "event_type": "object.updated",
                    "source": "host",
                    "project_id": "project",
                    "object": {"type": "object", "id": "1"},
                    "before": {"value": event_id},
                    "after": {"value": "changed"},
                    "occurred_at": "2026-07-15T10:30:00+08:00",
                }
            )
        )

    statuses = {item.source_event_id: item.status for item in engine.list_proposals("project")}
    assert statuses["first"] == "obsolete"
    assert statuses["second"] == "pending"
