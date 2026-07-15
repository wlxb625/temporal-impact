"""Bounded, explainable BFS impact propagation."""

from collections import deque

import networkx as nx

from temporal_impact.events import ChangeEvent
from temporal_impact.impact.models import ImpactLevel, ImpactReport, ImpactResult, PathEdge
from temporal_impact.shadow import ShadowNode, ShadowRelation

DISTANCE_DECAY = {1: 1.0, 2: 0.75, 3: 0.56}


def classify_impact(score: float) -> ImpactLevel:
    """Classify a normalized impact score using the documented thresholds."""
    if score >= 0.85:
        return "conflict"
    if score >= 0.65:
        return "high"
    if score >= 0.40:
        return "medium"
    return "low"


def change_strength(event: ChangeEvent) -> float:
    """Estimate strength from the event payload without inspecting host content."""
    if event.before == event.after:
        return 0.0
    return 1.0 if event.before is not None or event.after is not None else 0.5


class ImpactAnalyzer:
    """Propagate a change through valid relations while retaining every selected path."""

    def __init__(self, max_depth: int = 3) -> None:
        if max_depth < 1:
            msg = "max_depth must be at least 1"
            raise ValueError(msg)
        self.max_depth = min(max_depth, 3)

    def analyze(
        self, event: ChangeEvent, graph: nx.MultiDiGraph, nodes: list[ShadowNode]
    ) -> ImpactReport:
        """Produce the strongest explainable path for each affected target."""
        source_ids = [
            node.id
            for node in nodes
            if node.project_id == event.project_id
            and node.branch_id == event.branch_id
            and node.source_system == event.source
            and node.source_type == event.object.type
            and node.source_id == event.object.id
        ]
        report = ImpactReport(
            source_event_id=event.event_id,
            project_id=event.project_id,
            branch_id=event.branch_id,
            source_node_ids=source_ids,
        )
        strength = change_strength(event)
        if strength == 0.0:
            return report

        best_results: dict[str, ImpactResult] = {}
        for source_id in source_ids:
            self._walk(graph, source_id, strength, best_results)
        report.impacts = sorted(
            best_results.values(), key=lambda result: result.score, reverse=True
        )
        return report

    def _walk(
        self,
        graph: nx.MultiDiGraph,
        source_id: str,
        strength: float,
        best_results: dict[str, ImpactResult],
    ) -> None:
        queue: deque[tuple[str, float, list[PathEdge]]] = deque([(source_id, strength, [])])
        best_state: dict[tuple[str, int], float] = {(source_id, 0): strength}
        while queue:
            current_id, current_score, path = queue.popleft()
            depth = len(path)
            if depth >= self.max_depth:
                continue
            for _, target_id, _, data in graph.out_edges(current_id, keys=True, data=True):
                relation: ShadowRelation = data["relation"]
                target: ShadowNode = graph.nodes[target_id]["node"]
                if relation.status != "valid" or target.status in {"discarded", "locked"}:
                    continue
                if target_id in {edge.source_node_id for edge in path}:
                    continue
                next_depth = depth + 1
                edge = PathEdge(
                    relation_id=relation.id,
                    relation_type=relation.relation_type,
                    weight=relation.weight,
                    confidence=relation.confidence,
                    source_node_id=current_id,
                    target_node_id=target_id,
                )
                next_score = min(
                    1.0,
                    current_score
                    * relation.weight
                    * relation.confidence
                    * target.importance
                    * DISTANCE_DECAY[next_depth],
                )
                previous_score = best_state.get((target_id, next_depth), -1.0)
                if next_score <= previous_score:
                    continue
                best_state[(target_id, next_depth)] = next_score
                next_path = [*path, edge]
                result = ImpactResult(
                    target_node_id=target_id,
                    score=next_score,
                    level=classify_impact(next_score),
                    distance=next_depth,
                    path=next_path,
                    reason=(
                        f"{source_id} affects {target_id} via "
                        f"{' -> '.join(item.relation_type for item in next_path)}"
                    ),
                )
                existing_result = best_results.get(target_id)
                if existing_result is None or result.score > existing_result.score:
                    best_results[target_id] = result
                queue.append((target_id, next_score, next_path))
