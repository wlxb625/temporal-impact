"""Analyze a changed research sample window using the public SDK."""

from temporal_impact import ChangeEvent, ImpactEngine, ShadowNode, ShadowRelation

engine = ImpactEngine(database_url="sqlite://")
for node in [
    ShadowNode(
        id="sample",
        project_id="research",
        source_system="study",
        source_type="dataset",
        source_id="sample-years",
    ),
    ShadowNode(
        id="stats",
        project_id="research",
        source_system="study",
        source_type="table",
        source_id="descriptive",
    ),
    ShadowNode(
        id="regression",
        project_id="research",
        source_system="study",
        source_type="table",
        source_id="regression",
    ),
    ShadowNode(
        id="abstract",
        project_id="research",
        source_system="study",
        source_type="section",
        source_id="abstract",
    ),
]:
    engine.register_node(node)
for relation in [
    ShadowRelation(
        id="sample-stats",
        project_id="research",
        source_node_id="sample",
        target_node_id="stats",
        relation_type="depends_on",
        weight=0.9,
    ),
    ShadowRelation(
        id="sample-regression",
        project_id="research",
        source_node_id="sample",
        target_node_id="regression",
        relation_type="depends_on",
        weight=0.85,
    ),
    ShadowRelation(
        id="sample-abstract",
        project_id="research",
        source_node_id="sample",
        target_node_id="abstract",
        relation_type="references",
        weight=0.55,
    ),
]:
    engine.register_relation(relation)
event = ChangeEvent.model_validate(
    {
        "event_id": "sample-window",
        "event_type": "object.updated",
        "source": "study",
        "project_id": "research",
        "object": {"type": "dataset", "id": "sample-years"},
        "before": {"years": "2015-2024"},
        "after": {"years": "2018-2024"},
        "occurred_at": "2026-07-15T10:30:00+08:00",
    }
)
print(engine.analyze(event).model_dump_json(indent=2))
