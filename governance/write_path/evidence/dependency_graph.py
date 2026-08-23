"""
Phase 2: Dependency Graph Implementation
UP-TEST-003 V3.2 Evidence State Machine Extension

Implements DependencyEdge data structure and edge management functions
for tracking blocking evidence and open dependencies in the state machine.

Design Reference: HGD-UP-TEST-003-V3-2-PHASE1-DESIGN-COMPLETE-001.md
Phase 2 Scope: Dependency Graph Implementation (Days 1-4)
"""

from typing import TypedDict, List, Optional, Dict
from datetime import datetime


class DependencyEdge(TypedDict):
    """
    Tracks a dependency relationship between two evidence records.

    Used to maintain the dependency graph that shows which evidence blocks
    other evidence from transitioning out of UNKNOWN state.
    """
    dependency_id: str        # Unique identifier (DEP-001, DEP-002, etc.)
    source_evidence: str      # Evidence ID that is blocked (cannot resolve)
    target_evidence: str      # Evidence ID that blocks it (must be resolved)
    status: str              # "OPEN" (blocking) or "RESOLVED" (no longer blocking)
    created_at: str          # ISO8601 UTC timestamp
    created_by: str          # Actor who created the dependency
    resolved_at: Optional[str]  # ISO8601 UTC when resolved (None if OPEN)
    resolved_by: Optional[str]  # Actor who resolved the dependency


class DependencyGraphStore:
    """
    In-memory store for dependency edges.

    In production, this would be backed by a database table.
    For Phase 2 testing (E3.1, E3.2), in-memory storage is sufficient.
    """

    def __init__(self):
        """Initialize empty dependency graph."""
        self._edges: Dict[str, DependencyEdge] = {}
        self._source_index: Dict[str, List[str]] = {}  # source_id -> [dep_ids]
        self._target_index: Dict[str, List[str]] = {}  # target_id -> [dep_ids]

    def add_edge(
        self,
        dependency_id: str,
        source_evidence: str,
        target_evidence: str,
        created_by: str = "system",
        status: str = "OPEN"
    ) -> DependencyEdge:
        """
        Add a new dependency edge to the graph.

        Args:
            dependency_id: Unique identifier for this dependency
            source_evidence: Evidence ID that is blocked
            target_evidence: Evidence ID that blocks it
            created_by: Actor creating this edge
            status: "OPEN" or "RESOLVED"

        Returns:
            The created DependencyEdge

        Raises:
            ValueError: If dependency_id already exists
        """
        if dependency_id in self._edges:
            raise ValueError(f"Dependency {dependency_id} already exists")

        edge: DependencyEdge = {
            "dependency_id": dependency_id,
            "source_evidence": source_evidence,
            "target_evidence": target_evidence,
            "status": status,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "created_by": created_by,
            "resolved_at": None,
            "resolved_by": None,
        }

        self._edges[dependency_id] = edge

        # Update indices
        if source_evidence not in self._source_index:
            self._source_index[source_evidence] = []
        self._source_index[source_evidence].append(dependency_id)

        if target_evidence not in self._target_index:
            self._target_index[target_evidence] = []
        self._target_index[target_evidence].append(dependency_id)

        return edge

    def get_edge(self, dependency_id: str) -> Optional[DependencyEdge]:
        """Retrieve a dependency edge by ID."""
        return self._edges.get(dependency_id)

    def resolve_edge(self, dependency_id: str, resolved_by: str = "system") -> DependencyEdge:
        """
        Mark a dependency edge as resolved.

        Args:
            dependency_id: ID of the edge to resolve
            resolved_by: Actor resolving this edge

        Returns:
            The updated DependencyEdge

        Raises:
            ValueError: If dependency_id doesn't exist
        """
        if dependency_id not in self._edges:
            raise ValueError(f"Dependency {dependency_id} not found")

        edge = self._edges[dependency_id]
        edge["status"] = "RESOLVED"
        edge["resolved_at"] = datetime.utcnow().isoformat() + "Z"
        edge["resolved_by"] = resolved_by

        return edge

    def remove_edge(self, dependency_id: str) -> bool:
        """
        Remove a dependency edge from the graph.

        Args:
            dependency_id: ID of the edge to remove

        Returns:
            True if edge existed and was removed, False otherwise
        """
        if dependency_id not in self._edges:
            return False

        edge = self._edges[dependency_id]

        # Remove from indices
        if edge["source_evidence"] in self._source_index:
            self._source_index[edge["source_evidence"]].remove(dependency_id)
        if edge["target_evidence"] in self._target_index:
            self._target_index[edge["target_evidence"]].remove(dependency_id)

        del self._edges[dependency_id]
        return True

    def get_blocking_chain(
        self,
        evidence_id: str,
        max_depth: Optional[int] = None
    ) -> List[str]:
        """
        Get the chain of evidence IDs that block the given evidence.

        Performs a depth-first traversal of the dependency graph starting
        from the source evidence and collecting all target evidence IDs
        that it depends on (directly or transitively).

        Args:
            evidence_id: The evidence whose blockers to find
            max_depth: Maximum traversal depth (None for unlimited)

        Returns:
            List of evidence IDs that block the given evidence,
            in order of discovery (depth-first traversal)

        E3.1 Test Case: Single-level dependency
            Evidence EVI-001 has 1 blocker (EVI-002)
            get_blocking_chain("EVI-001") -> ["EVI-002"]

        E3.2 Test Case: Multi-level dependency (depth 1-3)
            Chain: EVI-001 -> EVI-002 -> EVI-003 -> EVI-004
            get_blocking_chain("EVI-001", max_depth=3) -> ["EVI-002", "EVI-003", "EVI-004"]
        """
        visited = set()
        blocking_chain = []

        def traverse(source_id: str, depth: int = 0):
            """Recursive depth-first traversal."""
            if max_depth is not None and depth >= max_depth:
                return

            if source_id not in self._source_index:
                return

            # Get all edges where this evidence is the source (blocked by someone)
            edge_ids = self._source_index[source_id]

            for edge_id in edge_ids:
                edge = self._edges[edge_id]

                # Only follow OPEN dependencies
                if edge["status"] != "OPEN":
                    continue

                target = edge["target_evidence"]

                if target not in visited:
                    visited.add(target)
                    blocking_chain.append(target)
                    # Recursively find what blocks this target
                    traverse(target, depth + 1)

        traverse(evidence_id)
        return blocking_chain

    def get_dependencies(
        self,
        evidence_id: str,
        depth: int = 1
    ) -> List[str]:
        """
        Get dependencies at a specific depth level.

        Args:
            evidence_id: The evidence whose dependencies to find
            depth: Traversal depth (1 for immediate, 2 for next level, etc.)

        Returns:
            List of evidence IDs at the specified depth level

        E3.2 Test Case: Depth-specific dependencies
            Chain: EVI-001 -> EVI-002 -> EVI-003 -> EVI-004
            get_dependencies("EVI-001", depth=1) -> ["EVI-002"]
            get_dependencies("EVI-001", depth=2) -> ["EVI-003"]
            get_dependencies("EVI-001", depth=3) -> ["EVI-004"]
        """
        current_level = {evidence_id}

        for _ in range(depth):
            next_level = set()

            for source_id in current_level:
                if source_id not in self._source_index:
                    continue

                edge_ids = self._source_index[source_id]
                for edge_id in edge_ids:
                    edge = self._edges[edge_id]
                    if edge["status"] == "OPEN":
                        next_level.add(edge["target_evidence"])

            current_level = next_level

        return list(current_level)

    def get_open_dependencies(self, evidence_id: str) -> List[str]:
        """
        Get all OPEN dependency IDs for the given evidence.

        Used to populate the open_dependencies field in EvidenceRecord.

        Args:
            evidence_id: The evidence whose open dependencies to find

        Returns:
            List of OPEN dependency IDs where this evidence is the source
        """
        if evidence_id not in self._source_index:
            return []

        open_deps = []
        for edge_id in self._source_index[evidence_id]:
            edge = self._edges[edge_id]
            if edge["status"] == "OPEN":
                open_deps.append(edge_id)

        return open_deps

    def get_all_edges(self) -> List[DependencyEdge]:
        """Get all dependency edges (for debugging and testing)."""
        return list(self._edges.values())

    def get_open_edges(self) -> List[DependencyEdge]:
        """Get all OPEN dependency edges."""
        return [edge for edge in self._edges.values() if edge["status"] == "OPEN"]

    def stats(self) -> Dict:
        """Get statistics about the dependency graph."""
        open_count = sum(1 for edge in self._edges.values() if edge["status"] == "OPEN")
        resolved_count = len(self._edges) - open_count

        return {
            "total_edges": len(self._edges),
            "open_edges": open_count,
            "resolved_edges": resolved_count,
            "source_evidence_count": len(self._source_index),
            "target_evidence_count": len(self._target_index),
        }


# Global store instance for Phase 2 testing
_dependency_store = DependencyGraphStore()


def get_store() -> DependencyGraphStore:
    """Get the global dependency graph store."""
    return _dependency_store
