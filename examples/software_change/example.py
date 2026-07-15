"""Analyze removal of an API currency field with the same SDK."""

from temporal_impact import ChangeEvent, ImpactEngine, ShadowNode, ShadowRelation

engine = ImpactEngine(database_url="sqlite://")
for node in [
    ShadowNode(
        id="currency",
        project_id="software",
        source_system="billing",
        source_type="api_field",
        source_id="currency",
    ),
    ShadowNode(
        id="frontend",
        project_id="software",
        source_system="billing",
        source_type="typescript",
        source_id="money.ts",
    ),
    ShadowNode(
        id="tests",
        project_id="software",
        source_system="billing",
        source_type="test",
        source_id="checkout",
    ),
    ShadowNode(
        id="docs",
        project_id="software",
        source_system="billing",
        source_type="document",
        source_id="api",
    ),
]:
    engine.register_node(node)
for relation in [
    ShadowRelation(
        id="currency-frontend",
        project_id="software",
        source_node_id="currency",
        target_node_id="frontend",
        relation_type="depends_on",
        weight=0.9,
    ),
    ShadowRelation(
        id="currency-tests",
        project_id="software",
        source_node_id="currency",
        target_node_id="tests",
        relation_type="depends_on",
        weight=0.8,
    ),
    ShadowRelation(
        id="currency-docs",
        project_id="software",
        source_node_id="currency",
        target_node_id="docs",
        relation_type="references",
        weight=0.6,
    ),
]:
    engine.register_relation(relation)
event = ChangeEvent.model_validate(
    {
        "event_id": "remove-currency",
        "event_type": "object.deleted",
        "source": "billing",
        "project_id": "software",
        "object": {"type": "api_field", "id": "currency"},
        "before": {"type": "string"},
        "after": None,
        "occurred_at": "2026-07-15T10:30:00+08:00",
    }
)
print(engine.analyze(event).model_dump_json(indent=2))
