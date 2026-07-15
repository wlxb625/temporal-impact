"""Derive read-only suggestions from explainable impact results."""

from temporal_impact.impact import ImpactReport
from temporal_impact.proposals.models import Proposal, ProposalType


class ProposalEngine:
    """Create deterministic, deduplicable suggestions without host side effects."""

    def generate(self, report: ImpactReport) -> list[Proposal]:
        """Generate only the suggestions warranted by each impact level."""
        proposals: list[Proposal] = []
        for impact in report.impacts:
            types: list[ProposalType] = ["recalculate_required"]
            if impact.level in {"medium", "high", "conflict"}:
                types.append("review_required")
            if impact.level in {"high", "conflict"}:
                types.extend(["mark_stale", "create_revision_task"])
            if impact.level == "conflict":
                types.append("branch_recommended")
            for proposal_type in types:
                proposals.append(
                    Proposal(
                        id=Proposal.stable_id(
                            report.source_event_id, impact.target_node_id, proposal_type
                        ),
                        project_id=report.project_id,
                        branch_id=report.branch_id,
                        source_event_id=report.source_event_id,
                        target_node_id=impact.target_node_id,
                        proposal_type=proposal_type,
                        priority=impact.score,
                        reason=impact.reason,
                        evidence=[edge.model_dump() for edge in impact.path],
                    )
                )
        return proposals
