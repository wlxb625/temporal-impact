"""Recalculate observations only for report targets marked by propagation."""

from temporal_impact.impact import ImpactReport
from temporal_impact.observations.models import (
    ObservationDependency,
    ObservationKind,
    ObservationValue,
)


class ObservationEngine:
    """Create compact scores from explainable impact results."""

    def recalculate(
        self,
        report: ImpactReport,
        existing_values: dict[str, ObservationValue],
    ) -> tuple[list[ObservationValue], list[ObservationDependency]]:
        """Return values only for affected targets, leaving unrelated values untouched."""
        values: list[ObservationValue] = []
        dependencies: list[ObservationDependency] = []
        for impact in report.impacts:
            scores: dict[ObservationKind, float] = {
                "conflict_score": impact.score,
                "staleness_score": impact.score if impact.level in {"conflict", "high"} else 0.0,
                "stability_score": 1.0 - impact.score,
            }
            for kind, value in scores.items():
                observation_id = f"{impact.target_node_id}:{kind}"
                previous = existing_values.get(observation_id)
                values.append(
                    ObservationValue(
                        id=observation_id,
                        project_id=report.project_id,
                        branch_id=report.branch_id,
                        target_node_id=impact.target_node_id,
                        kind=kind,
                        value=value,
                        previous_value=previous.value if previous else None,
                        source_event_id=report.source_event_id,
                    )
                )
                dependencies.extend(
                    ObservationDependency(
                        observation_id=observation_id,
                        node_id=edge.target_node_id,
                        relation_id=edge.relation_id,
                    )
                    for edge in impact.path
                )
        return values, dependencies
