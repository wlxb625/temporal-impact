# Temporal Impact

An embeddable, event-driven impact analysis engine for evolving applications.

Temporal Impact receives host-system changes, maintains a shadow dependency graph, and
will produce explainable impact proposals. It is designed to remain read-only by default:
the host application stays the source of truth.

> Status: `v0.1.0-alpha`. The local SDK, CLI, FastAPI sidecar, and Streamlit demo are ready.

## Install for development

```bash
python -m pip install -e ".[dev]"
```

Verify the package import:

```bash
python -c "import temporal_impact; print(temporal_impact.__version__)"
```

Validate an event JSON file:

```bash
temporal-impact ingest event.json
```

## Quick start

```python
from temporal_impact import ChangeEvent, ImpactEngine, ShadowNode, ShadowRelation

engine = ImpactEngine(database_url="sqlite:///impact.db")
engine.register_node(ShadowNode(id="master", project_id="novel", source_system="app", source_type="character", source_id="master"))
engine.register_node(ShadowNode(id="chapter-12", project_id="novel", source_system="app", source_type="chapter", source_id="12"))
engine.register_relation(ShadowRelation(id="r1", project_id="novel", source_node_id="master", target_node_id="chapter-12", relation_type="conflicts_with", weight=0.94))
report = engine.analyze(ChangeEvent.model_validate({"event_id":"evt-1","event_type":"object.updated","source":"app","project_id":"novel","object":{"type":"character","id":"master"},"before":{"status":"dead"},"after":{"status":"hidden_alive"},"occurred_at":"2026-07-15T10:30:00+08:00"}))
print(report.impacts)
```

Run the offline demonstration:

```bash
temporal-impact demo
```

It includes the fixed “师父死亡 → 师父假死” scenario and never writes to a host system.

## Interfaces

- SDK: `ImpactEngine`, `ChangeEvent`, `ShadowNode`, `ShadowRelation`, `ImpactReport`
- CLI: `init`, `ingest`, `analyze`, `graph`, `proposals`, `serve`, `demo`
- API: `/health`, `/events`, `/analyze`, `/reports/{report_id}`, graph and proposal routes
- Examples: [novel](examples/novel_adapter), [software](examples/software_change), and [research](examples/research_change)

## Documentation

- [Event schema](docs/EVENT_SCHEMA.md)
- [Adapter guide](docs/ADAPTER_GUIDE.md)
- [Algorithm](docs/ALGORITHM.md)
- [Integration guide](docs/INTEGRATION_GUIDE.md)

## Core capabilities

- Standard host change events
- Shadow nodes and dependency relations
- Explainable, bounded impact propagation
- Incremental observations and review proposals
- Python SDK, CLI, FastAPI sidecar, and Streamlit demonstration

## Development

The implementation is delivered one documented goal at a time. See
[the development plan](docs/DEVELOPMENT.md) and the repository contribution rules in
[AGENTS.md](AGENTS.md).

## License

Licensed under the [Apache License 2.0](LICENSE).
