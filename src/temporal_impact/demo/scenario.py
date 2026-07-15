"""Deterministic novel scenario used by the local Streamlit demo."""

from temporal_impact import ChangeEvent, ImpactEngine, ShadowNode, ShadowRelation


def load_story(engine: ImpactEngine) -> None:
    """Register a fixed, local-only shadow graph for the master false-death story."""
    for node in [
        ShadowNode(
            id="master",
            project_id="novel-demo",
            source_system="novel",
            source_type="character",
            source_id="master",
            summary="师父被宣布死亡",
        ),
        ShadowNode(
            id="chapter-12",
            project_id="novel-demo",
            source_system="novel",
            source_type="chapter",
            source_id="12",
            summary="主角复仇动机",
        ),
        ShadowNode(
            id="chapter-20",
            project_id="novel-demo",
            source_system="novel",
            source_type="chapter",
            source_id="20",
            summary="高潮对决",
        ),
    ]:
        engine.register_node(node)
    for relation in [
        ShadowRelation(
            id="master-ch12",
            project_id="novel-demo",
            source_node_id="master",
            target_node_id="chapter-12",
            relation_type="conflicts_with",
            weight=0.94,
        ),
        ShadowRelation(
            id="master-ch20",
            project_id="novel-demo",
            source_node_id="master",
            target_node_id="chapter-20",
            relation_type="depends_on",
            weight=0.86,
        ),
    ]:
        engine.register_relation(relation)


def false_death_event() -> ChangeEvent:
    """Return the fixed change: master death becomes hidden survival."""
    return ChangeEvent.model_validate(
        {
            "event_id": "demo-master-alive",
            "event_type": "object.updated",
            "source": "novel",
            "project_id": "novel-demo",
            "object": {"type": "character", "id": "master"},
            "before": {"status": "dead"},
            "after": {"status": "hidden_alive"},
            "occurred_at": "2026-07-15T10:30:00+08:00",
        }
    )
