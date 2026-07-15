"""SQLite persistence for compact Temporal Impact records."""

from collections.abc import Iterable
from pathlib import Path

from sqlmodel import Field, Session, SQLModel, create_engine, select

from temporal_impact.events import ChangeEvent
from temporal_impact.impact import ImpactReport
from temporal_impact.observations import ObservationDependency, ObservationValue
from temporal_impact.proposals import Proposal
from temporal_impact.shadow import ShadowNode, ShadowRelation


class EventRecord(SQLModel, table=True):
    """Persist a validated host event as JSON for traceability."""

    __tablename__ = "events"

    event_id: str = Field(primary_key=True)
    project_id: str
    branch_id: str
    payload: str


class ShadowNodeRecord(SQLModel, table=True):
    """Persist one shadow node as a compact JSON payload."""

    __tablename__ = "shadow_nodes"

    id: str = Field(primary_key=True)
    project_id: str
    branch_id: str
    payload: str


class ShadowRelationRecord(SQLModel, table=True):
    """Persist one directed shadow relation as JSON."""

    __tablename__ = "shadow_relations"

    id: str = Field(primary_key=True)
    project_id: str
    branch_id: str
    payload: str


class ImpactReportRecord(SQLModel, table=True):
    """Persist one analysis report and its explanation payload."""

    __tablename__ = "impact_reports"

    id: str = Field(primary_key=True)
    source_event_id: str = Field(index=True)
    project_id: str
    branch_id: str
    payload: str


class ImpactResultRecord(SQLModel, table=True):
    """Persist each report target separately for query-friendly impact history."""

    __tablename__ = "impact_results"

    id: str = Field(primary_key=True)
    report_id: str = Field(index=True)
    target_node_id: str = Field(index=True)
    payload: str


class ObservationValueRecord(SQLModel, table=True):
    """Persist the latest value for a target observation."""

    __tablename__ = "observation_values"

    id: str = Field(primary_key=True)
    project_id: str
    branch_id: str
    target_node_id: str
    kind: str
    payload: str


class ObservationDependencyRecord(SQLModel, table=True):
    """Persist a dependency row for observation traceability."""

    __tablename__ = "observation_dependencies"

    id: str = Field(primary_key=True)
    observation_id: str = Field(index=True)
    payload: str


class ProposalRecord(SQLModel, table=True):
    """Persist a local, read-only proposal."""

    __tablename__ = "proposals"

    id: str = Field(primary_key=True)
    project_id: str
    branch_id: str
    target_node_id: str = Field(index=True)
    status: str
    payload: str


class Repository:
    """Small transactional repository isolated from graph and UI concerns."""

    def __init__(self, database_url: str) -> None:
        if database_url.startswith("sqlite:///"):
            database_file = database_url.removeprefix("sqlite:///")
            if database_file != ":memory:":
                Path(database_file).expanduser().parent.mkdir(parents=True, exist_ok=True)
        self._engine = create_engine(database_url, connect_args={"check_same_thread": False})
        SQLModel.metadata.create_all(self._engine)

    def save_event(self, event: ChangeEvent) -> bool:
        """Save an event once and return whether it was newly accepted."""
        with Session(self._engine) as session:
            if session.get(EventRecord, event.event_id) is not None:
                return False
            session.add(
                EventRecord(
                    event_id=event.event_id,
                    project_id=event.project_id,
                    branch_id=event.branch_id,
                    payload=event.to_json(),
                )
            )
            session.commit()
        return True

    def get_event(self, event_id: str) -> ChangeEvent | None:
        """Retrieve a previously saved event."""
        with Session(self._engine) as session:
            record = session.get(EventRecord, event_id)
            return ChangeEvent.from_json(record.payload) if record else None

    def upsert_node(self, node: ShadowNode) -> None:
        """Create or replace a compact shadow-node record atomically."""
        with Session(self._engine) as session:
            session.merge(
                ShadowNodeRecord(
                    id=node.id,
                    project_id=node.project_id,
                    branch_id=node.branch_id,
                    payload=node.model_dump_json(exclude_none=True),
                )
            )
            session.commit()

    def get_node(self, node_id: str) -> ShadowNode | None:
        """Retrieve a node by its stable shadow identifier."""
        with Session(self._engine) as session:
            record = session.get(ShadowNodeRecord, node_id)
            return ShadowNode.model_validate_json(record.payload) if record else None

    def list_nodes(self, project_id: str, branch_id: str = "main") -> list[ShadowNode]:
        """List only nodes belonging to a project branch."""
        with Session(self._engine) as session:
            statement = select(ShadowNodeRecord).where(
                ShadowNodeRecord.project_id == project_id,
                ShadowNodeRecord.branch_id == branch_id,
            )
            records = session.exec(statement)
            return [ShadowNode.model_validate_json(record.payload) for record in records]

    def upsert_relation(self, relation: ShadowRelation) -> None:
        """Create or replace a shadow relation atomically."""
        with Session(self._engine) as session:
            session.merge(
                ShadowRelationRecord(
                    id=relation.id,
                    project_id=relation.project_id,
                    branch_id=relation.branch_id,
                    payload=relation.model_dump_json(exclude_none=True),
                )
            )
            session.commit()

    def list_relations(self, project_id: str, branch_id: str = "main") -> list[ShadowRelation]:
        """List a project branch's relations without dereferencing host data."""
        with Session(self._engine) as session:
            statement = select(ShadowRelationRecord).where(
                ShadowRelationRecord.project_id == project_id,
                ShadowRelationRecord.branch_id == branch_id,
            )
            records = session.exec(statement)
            return [ShadowRelation.model_validate_json(record.payload) for record in records]

    def replace_nodes(self, nodes: Iterable[ShadowNode]) -> None:
        """Store a sequence of nodes through the normal transactional path."""
        for node in nodes:
            self.upsert_node(node)

    def save_report(self, report: ImpactReport) -> None:
        """Persist a report once its impact traversal is complete."""
        with Session(self._engine) as session:
            session.merge(
                ImpactReportRecord(
                    id=report.id,
                    source_event_id=report.source_event_id,
                    project_id=report.project_id,
                    branch_id=report.branch_id,
                    payload=report.model_dump_json(),
                )
            )
            for result in report.impacts:
                session.merge(
                    ImpactResultRecord(
                        id=f"{report.id}:{result.target_node_id}",
                        report_id=report.id,
                        target_node_id=result.target_node_id,
                        payload=result.model_dump_json(),
                    )
                )
            session.commit()

    def get_report(self, report_id: str) -> ImpactReport | None:
        """Load one report by its identifier."""
        with Session(self._engine) as session:
            record = session.get(ImpactReportRecord, report_id)
            return ImpactReport.model_validate_json(record.payload) if record else None

    def get_report_for_event(self, event_id: str) -> ImpactReport | None:
        """Retrieve the earlier report for an idempotently submitted event."""
        with Session(self._engine) as session:
            statement = select(ImpactReportRecord).where(
                ImpactReportRecord.source_event_id == event_id
            )
            record = session.exec(statement).first()
            return ImpactReport.model_validate_json(record.payload) if record else None

    def get_observations(self, project_id: str, branch_id: str = "main") -> list[ObservationValue]:
        """List current observation values for a project branch."""
        with Session(self._engine) as session:
            statement = select(ObservationValueRecord).where(
                ObservationValueRecord.project_id == project_id,
                ObservationValueRecord.branch_id == branch_id,
            )
            records = session.exec(statement)
            return [ObservationValue.model_validate_json(item.payload) for item in records]

    def save_observations(
        self, values: Iterable[ObservationValue], dependencies: Iterable[ObservationDependency]
    ) -> None:
        """Persist recalculated values and their compact dependency evidence together."""
        with Session(self._engine) as session:
            for value in values:
                session.merge(
                    ObservationValueRecord(
                        id=value.id,
                        project_id=value.project_id,
                        branch_id=value.branch_id,
                        target_node_id=value.target_node_id,
                        kind=value.kind,
                        payload=value.model_dump_json(),
                    )
                )
            for dependency in dependencies:
                relation_id = dependency.relation_id or "node"
                dependency_id = f"{dependency.observation_id}:{dependency.node_id}:{relation_id}"
                session.merge(
                    ObservationDependencyRecord(
                        id=dependency_id,
                        observation_id=dependency.observation_id,
                        payload=dependency.model_dump_json(),
                    )
                )
            session.commit()

    def save_proposals(self, proposals: Iterable[Proposal]) -> None:
        """Persist deterministic proposal IDs without duplicating suggestions."""
        with Session(self._engine) as session:
            for proposal in proposals:
                if session.get(ProposalRecord, proposal.id) is None:
                    session.add(
                        ProposalRecord(
                            id=proposal.id,
                            project_id=proposal.project_id,
                            branch_id=proposal.branch_id,
                            target_node_id=proposal.target_node_id,
                            status=proposal.status,
                            payload=proposal.model_dump_json(),
                        )
                    )
            session.commit()

    def obsolete_pending_proposals(self, target_node_id: str, source_event_id: str) -> None:
        """Invalidate pending suggestions superseded by a newer event for the same target."""
        with Session(self._engine) as session:
            statement = select(ProposalRecord).where(
                ProposalRecord.target_node_id == target_node_id,
                ProposalRecord.status == "pending",
            )
            for record in session.exec(statement):
                proposal = Proposal.model_validate_json(record.payload)
                if proposal.source_event_id != source_event_id:
                    obsolete = proposal.model_copy(update={"status": "obsolete"})
                    record.status = "obsolete"
                    record.payload = obsolete.model_dump_json()
                    session.add(record)
            session.commit()

    def list_proposals(self, project_id: str, branch_id: str = "main") -> list[Proposal]:
        """List proposals for a project branch."""
        with Session(self._engine) as session:
            statement = select(ProposalRecord).where(
                ProposalRecord.project_id == project_id,
                ProposalRecord.branch_id == branch_id,
            )
            return [Proposal.model_validate_json(item.payload) for item in session.exec(statement)]

    def update_proposal_status(self, proposal_id: str, status: str) -> Proposal | None:
        """Update local proposal status only; no host write is attempted."""
        with Session(self._engine) as session:
            record = session.get(ProposalRecord, proposal_id)
            if record is None:
                return None
            proposal = Proposal.model_validate_json(record.payload).model_copy(
                update={"status": status}
            )
            record.status = status
            record.payload = proposal.model_dump_json()
            session.add(record)
            session.commit()
            return proposal
