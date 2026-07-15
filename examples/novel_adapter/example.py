"""Run the deterministic false-death example through the public SDK."""

from temporal_impact import ImpactEngine
from temporal_impact.demo import false_death_event, load_story

engine = ImpactEngine(database_url="sqlite://")
load_story(engine)
report = engine.analyze(false_death_event())
print(report.model_dump_json(indent=2))
