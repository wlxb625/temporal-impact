"""Integration coverage for SQLite shadow persistence and graph building."""

from pathlib import Path

from temporal_impact.events import ChangeEvent
from temporal_impact.graph import build_shadow_graph
from temporal_impact.shadow import ShadowNode, ShadowRelation
from temporal_impact.storage import Repository


def test_sqlite_persists_events_nodes_and_relations(tmp_path: Path) -> None:
    """A fresh repository instance reads records written by an earlier instance."""
    database_url = f"sqlite:///{tmp_path / 'impact.db'}"
    repository = Repository(database_url)
    event = ChangeEvent.model_validate(
        {
            "event_id": "evt-storage",
            "event_type": "object.updated",
            "source": "host",
            "project_id": "project",
            "object": {"type": "chapter", "id": "12"},
            "occurred_at": "2026-07-15T10:30:00+08:00",
        }
    )
    source = ShadowNode(
        id="master",
        project_id="project",
        source_system="host",
        source_type="character",
        source_id="1",
    )
    target = ShadowNode(
        id="chapter-12",
        project_id="project",
        source_system="host",
        source_type="chapter",
        source_id="12",
    )
    relation = ShadowRelation(
        id="rel-1",
        project_id="project",
        source_node_id="master",
        target_node_id="chapter-12",
        relation_type="conflicts_with",
    )

    assert repository.save_event(event)
    assert not repository.save_event(event)
    repository.upsert_node(source)
    repository.upsert_node(target)
    repository.upsert_relation(relation)

    reopened = Repository(database_url)
    assert reopened.get_event(event.event_id) == event
    nodes = reopened.list_nodes("project")
    relations = reopened.list_relations("project")
    graph = build_shadow_graph(nodes, relations)
    assert set(graph.nodes) == {"master", "chapter-12"}
    assert graph.has_edge("master", "chapter-12", key="rel-1")
