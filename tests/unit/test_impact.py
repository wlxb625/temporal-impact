"""Unit tests for bounded, explainable impact propagation."""

from temporal_impact.events import ChangeEvent
from temporal_impact.graph import build_shadow_graph
from temporal_impact.impact import ImpactAnalyzer, classify_impact
from temporal_impact.shadow import ShadowNode, ShadowRelation


def node(node_id: str, importance: float = 1.0, status: str = "valid") -> ShadowNode:
    """Build a shadow node for propagation tests."""
    source_type = "character" if node_id == "master" else "chapter"
    return ShadowNode(
        id=node_id,
        project_id="project",
        source_system="host",
        source_type=source_type,
        source_id=node_id,
        importance=importance,
        status=status,  # type: ignore[arg-type]
    )


def relation(source: str, target: str, relation_id: str, weight: float = 1.0) -> ShadowRelation:
    """Build a valid relation for a propagation test."""
    return ShadowRelation(
        id=relation_id,
        project_id="project",
        source_node_id=source,
        target_node_id=target,
        relation_type="depends_on",
        weight=weight,
    )


def event() -> ChangeEvent:
    """Return a source change matching the master shadow node."""
    return ChangeEvent.model_validate(
        {
            "event_id": "evt-impact",
            "event_type": "object.updated",
            "source": "host",
            "project_id": "project",
            "object": {"type": "character", "id": "master"},
            "before": {"status": "dead"},
            "after": {"status": "hidden_alive"},
            "occurred_at": "2026-07-15T10:30:00+08:00",
        }
    )


def test_propagation_keeps_best_complete_path_and_handles_cycle() -> None:
    """A cycle cannot loop forever and a target keeps its strongest path."""
    nodes = [node("master"), node("chapter-12"), node("chapter-20")]
    relations = [
        relation("master", "chapter-12", "r1", 0.9),
        relation("chapter-12", "chapter-20", "r2", 0.9),
        relation("chapter-20", "master", "r3", 1.0),
        relation("master", "chapter-20", "r4", 0.8),
    ]

    report = ImpactAnalyzer().analyze(event(), build_shadow_graph(nodes, relations), nodes)

    impacts = {impact.target_node_id: impact for impact in report.impacts}
    assert set(impacts) == {"chapter-12", "chapter-20"}
    assert impacts["chapter-20"].distance == 1
    assert [edge.relation_id for edge in impacts["chapter-20"].path] == ["r4"]


def test_propagation_respects_depth_invalid_relations_and_locks() -> None:
    """Non-traversable targets are excluded and depth is bounded at three."""
    nodes = [
        node("master"),
        node("one"),
        node("two"),
        node("three"),
        node("four"),
        node("locked", status="locked"),
    ]
    relations = [
        relation("master", "one", "r1"),
        relation("one", "two", "r2"),
        relation("two", "three", "r3"),
        relation("three", "four", "r4"),
        relation("master", "locked", "r5"),
    ]

    report = ImpactAnalyzer().analyze(event(), build_shadow_graph(nodes, relations), nodes)

    assert {impact.target_node_id for impact in report.impacts} == {"one", "two", "three"}


def test_impact_classification_thresholds() -> None:
    """Documented score bands remain stable."""
    assert classify_impact(0.85) == "conflict"
    assert classify_impact(0.65) == "high"
    assert classify_impact(0.40) == "medium"
    assert classify_impact(0.39) == "low"
