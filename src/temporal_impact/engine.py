"""High-level orchestration for the read-only Temporal Impact workflow."""

from temporal_impact.config import Settings
from temporal_impact.events import ChangeEvent
from temporal_impact.graph import build_shadow_graph
from temporal_impact.impact import ImpactAnalyzer, ImpactReport
from temporal_impact.observations import ObservationEngine
from temporal_impact.proposals import Proposal, ProposalEngine
from temporal_impact.shadow import ShadowNode, ShadowRelation
from temporal_impact.storage import Repository


class ImpactEngine:
    """Register shadow data, ingest events, and generate explainable local outputs."""

    def __init__(
        self,
        database_url: str | None = None,
        max_depth: int | None = None,
        default_branch: str = "main",
    ) -> None:
        settings = Settings()
        self.default_branch = default_branch
        self.repository = Repository(database_url or settings.database_url)
        self.analyzer = ImpactAnalyzer(max_depth or settings.max_depth)
        self.observation_engine = ObservationEngine()
        self.proposal_engine = ProposalEngine()

    def register_node(self, node: ShadowNode) -> None:
        """Store a compact shadow-node reference without reading host content."""
        self.repository.upsert_node(node)

    def register_relation(self, relation: ShadowRelation) -> None:
        """Store a weighted relationship between registered shadow nodes."""
        self.repository.upsert_relation(relation)

    def ingest(self, event: ChangeEvent) -> bool:
        """Persist one validated event; repeated IDs return ``False``."""
        return self.repository.save_event(event)

    def analyze(self, event: ChangeEvent) -> ImpactReport:
        """Run idempotent propagation and local observation/proposal generation."""
        newly_ingested = self.ingest(event)
        if not newly_ingested:
            existing_report = self.repository.get_report_for_event(event.event_id)
            if existing_report is not None:
                return existing_report
        nodes = self.repository.list_nodes(event.project_id, event.branch_id)
        relations = self.repository.list_relations(event.project_id, event.branch_id)
        report = self.analyzer.analyze(event, build_shadow_graph(nodes, relations), nodes)
        self.repository.save_report(report)
        existing_values = {
            value.id: value
            for value in self.repository.get_observations(event.project_id, event.branch_id)
        }
        values, dependencies = self.observation_engine.recalculate(report, existing_values)
        self.repository.save_observations(values, dependencies)
        proposals = self.proposal_engine.generate(report)
        for proposal in proposals:
            self.repository.obsolete_pending_proposals(proposal.target_node_id, event.event_id)
        self.repository.save_proposals(proposals)
        return report

    def get_report(self, report_id: str) -> ImpactReport | None:
        """Retrieve an explainable impact report."""
        return self.repository.get_report(report_id)

    def list_proposals(self, project_id: str, branch_id: str | None = None) -> list[Proposal]:
        """List locally stored proposals; this method never calls a host adapter."""
        return self.repository.list_proposals(project_id, branch_id or self.default_branch)

    def graph_data(self, project_id: str, branch_id: str | None = None) -> dict[str, object]:
        """Return a JSON-friendly project graph for interfaces."""
        branch = branch_id or self.default_branch
        nodes = self.repository.list_nodes(project_id, branch)
        relations = self.repository.list_relations(project_id, branch)
        return {
            "nodes": [node.model_dump(mode="json") for node in nodes],
            "relations": [relation.model_dump(mode="json") for relation in relations],
        }
