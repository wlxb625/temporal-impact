"""Host integration protocol; adapters never access host databases directly."""

from abc import ABC, abstractmethod
from typing import Any

from temporal_impact.shadow import ShadowNode, ShadowRelation


class HostAdapter(ABC):
    """The sole supported integration boundary for host-system data."""

    @abstractmethod
    def get_object(self, object_type: str, object_id: str) -> dict[str, Any]:
        """Read a host object through the host application's own service layer."""

    @abstractmethod
    def list_relations(self, object_type: str, object_id: str) -> list[dict[str, Any]]:
        """Read compact host relationship descriptors."""

    def apply_proposal(self, proposal: dict[str, Any]) -> None:
        """Optionally apply a user-confirmed proposal; v0.1 defaults to no-op support."""
        raise NotImplementedError("Host write-back must be explicitly implemented by an adapter")


class MemoryAdapter(HostAdapter):
    """In-memory adapter for tests and local integration examples."""

    def __init__(
        self,
        objects: dict[tuple[str, str], dict[str, Any]],
        relations: list[dict[str, Any]],
    ) -> None:
        self._objects = objects
        self._relations = relations

    def get_object(self, object_type: str, object_id: str) -> dict[str, Any]:
        """Return a test object or raise a helpful key error."""
        return self._objects[(object_type, object_id)]

    def list_relations(self, object_type: str, object_id: str) -> list[dict[str, Any]]:
        """Return relation descriptors whose source matches the requested object."""
        return [
            relation
            for relation in self._relations
            if relation["source_type"] == object_type and relation["source_id"] == object_id
        ]


class ShadowMapper:
    """Map host-service data to compact shadow representations."""

    def __init__(
        self,
        adapter: HostAdapter,
        source_system: str,
        project_id: str,
        branch_id: str = "main",
    ) -> None:
        self.adapter = adapter
        self.source_system = source_system
        self.project_id = project_id
        self.branch_id = branch_id

    def node(self, object_type: str, object_id: str) -> ShadowNode:
        """Map a host object using only explicitly supplied analysis metadata."""
        item = self.adapter.get_object(object_type, object_id)
        return ShadowNode(
            id=item.get("shadow_id", f"{self.source_system}:{object_type}:{object_id}"),
            project_id=self.project_id,
            branch_id=self.branch_id,
            source_system=self.source_system,
            source_type=object_type,
            source_id=object_id,
            source_revision=item.get("revision"),
            fingerprint=item.get("fingerprint"),
            summary=item.get("summary"),
            importance=item.get("importance", 1.0),
            status=item.get("status", "valid"),
        )

    def relations(self, object_type: str, object_id: str) -> list[ShadowRelation]:
        """Map host relationship descriptors without leaking host storage details."""
        return [
            ShadowRelation(
                id=item["id"],
                project_id=self.project_id,
                branch_id=self.branch_id,
                source_node_id=item["source_node_id"],
                target_node_id=item["target_node_id"],
                relation_type=item["relation_type"],
                weight=item.get("weight", 0.5),
                confidence=item.get("confidence", 1.0),
                status=item.get("status", "valid"),
                evidence=item.get("evidence"),
            )
            for item in self.adapter.list_relations(object_type, object_id)
        ]
