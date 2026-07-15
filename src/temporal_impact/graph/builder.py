"""NetworkX graph construction independent of persistence and interfaces."""

import networkx as nx

from temporal_impact.shadow import ShadowNode, ShadowRelation


def build_shadow_graph(nodes: list[ShadowNode], relations: list[ShadowRelation]) -> nx.MultiDiGraph:
    """Create a directed graph carrying only shadow metadata and relation evidence."""
    graph = nx.MultiDiGraph()
    for node in nodes:
        graph.add_node(node.id, node=node)
    for relation in relations:
        if relation.source_node_id in graph and relation.target_node_id in graph:
            graph.add_edge(
                relation.source_node_id,
                relation.target_node_id,
                key=relation.id,
                relation=relation,
            )
    return graph
