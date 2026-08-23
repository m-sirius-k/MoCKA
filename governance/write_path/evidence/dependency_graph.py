"""
HGD-UP-TEST-003-V3-2: Dependency Graph Implementation

Phase 2: Data Structures, API, Storage, State Management

Scope: Dependency Graph as specified in Phase1 Design Specification
Status: Implementation (not auto-inference, no scope expansion)
"""

import json
import uuid
import hashlib
from datetime import datetime
from enum import Enum
from typing import List, Dict, Set, Optional, Tuple
from pathlib import Path


class DependencyType(Enum):
    """Edge relationship types"""
    DEPENDS_ON = "depends_on"      # A depends on B
    IMPACTS = "impacts"             # A impacts B
    BLOCKS = "blocks"               # A blocks B
    PROVIDES = "provides"           # A provides to B


class VerificationStatus(Enum):
    """Verification status of dependency edges"""
    VERIFIED = "verified"           # Confirmed
    ASSUMED = "assumed"             # Assumed with evidence
    UNKNOWN = "unknown"             # Unconfirmed (preserved, not hidden)
    DISPUTED = "disputed"           # Multiple contradicting evidence


class GraphState(Enum):
    """Dependency Graph state transitions"""
    INIT = "init"                   # Initial
    RECORDING = "recording"         # Adding edges
    VERIFICATION = "verification"   # Verifying edges
    LOCKED = "locked"               # Read-only
    SEALED = "sealed"               # Archived


class DependencyEdge:
    """Immutable dependency edge record"""

    def __init__(
        self,
        from_component: str,
        to_component: str,
        relationship_type: DependencyType,
        metadata: Optional[Dict] = None,
    ):
        self.from_component = from_component
        self.to_component = to_component
        self.relationship_type = relationship_type
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "from": self.from_component,
            "to": self.to_component,
            "type": self.relationship_type.value,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    def __repr__(self) -> str:
        return f"DependencyEdge({self.from_component}->{self.to_component}:{self.relationship_type.value})"


class DependencyRecord:
    """Immutable record of dependency with verification metadata"""

    def __init__(
        self,
        edge: DependencyEdge,
        verification_status: VerificationStatus = VerificationStatus.ASSUMED,
        evidence_link: Optional[str] = None,
        comment: Optional[str] = None,
    ):
        self.record_id = str(uuid.uuid4())
        self.edge = edge
        self.recorded_at = datetime.utcnow().isoformat() + "Z"
        self.verification_status = verification_status
        self.evidence_link = evidence_link
        self.comment = comment or ""

    def compute_hash(self) -> str:
        """Compute SHA256 hash of record (for integrity verification)"""
        content = json.dumps(
            {
                "edge": self.edge.to_dict(),
                "status": self.verification_status.value,
                "evidence": self.evidence_link,
                "comment": self.comment,
                "recorded_at": self.recorded_at,
            },
            sort_keys=True,
        )
        return hashlib.sha256(content.encode()).hexdigest()

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            "record_id": self.record_id,
            "edge": self.edge.to_dict(),
            "recorded_at": self.recorded_at,
            "verification_status": self.verification_status.value,
            "evidence_link": self.evidence_link,
            "comment": self.comment,
            "hash": self.compute_hash(),
        }

    def __repr__(self) -> str:
        return f"DependencyRecord(id={self.record_id[:8]}, status={self.verification_status.value})"


class VerificationEvent:
    """Record of edge verification"""

    def __init__(
        self,
        record_id: str,
        verification_result: str,  # "pass" | "fail" | "inconclusive"
        verifier: str,
        evidence: str,
    ):
        self.event_id = str(uuid.uuid4())
        self.record_id = record_id
        self.verification_result = verification_result
        self.verifier = verifier
        self.evidence = evidence
        self.timestamp = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict:
        return {
            "event_id": self.event_id,
            "record_id": self.record_id,
            "verification_result": self.verification_result,
            "verifier": self.verifier,
            "evidence": self.evidence,
            "timestamp": self.timestamp,
        }


class ConflictRecord:
    """Record of detected conflicts (e.g., circular dependencies)"""

    def __init__(
        self,
        edge_ids: List[str],
        conflict_type: str,  # "circular_dependency" | "contradiction" | "mutual_blocking"
    ):
        self.conflict_id = str(uuid.uuid4())
        self.edge_ids = edge_ids
        self.conflict_type = conflict_type
        self.status = "open"
        self.timestamp = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict:
        return {
            "conflict_id": self.conflict_id,
            "edge_ids": self.edge_ids,
            "conflict_type": self.conflict_type,
            "status": self.status,
            "timestamp": self.timestamp,
        }


class DependencyGraph:
    """Append-only, immutable dependency graph storage and API"""

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize Dependency Graph

        Args:
            storage_path: Path to append-only JSONL storage (default: governance/write_path/evidence/dependency_graph.jsonl)
        """
        self.storage_path = storage_path or Path(
            "governance/write_path/evidence/dependency_graph.jsonl"
        )
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        self.records: List[DependencyRecord] = []
        self.state = GraphState.INIT
        self.components: Set[str] = set()
        self._load_from_storage()

    def _load_from_storage(self):
        """Load records from append-only JSONL file"""
        if not self.storage_path.exists():
            return

        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    # Reconstruct DependencyRecord from stored data
                    edge_data = data["edge"]
                    edge = DependencyEdge(
                        from_component=edge_data["from"],
                        to_component=edge_data["to"],
                        relationship_type=DependencyType(edge_data["type"]),
                        metadata=edge_data.get("metadata", {}),
                    )
                    edge.timestamp = edge_data["timestamp"]

                    record = DependencyRecord(
                        edge=edge,
                        verification_status=VerificationStatus(
                            data["verification_status"]
                        ),
                        evidence_link=data.get("evidence_link"),
                        comment=data.get("comment", ""),
                    )
                    record.record_id = data["record_id"]
                    record.recorded_at = data["recorded_at"]

                    # Verify hash integrity
                    stored_hash = data["hash"]
                    computed_hash = record.compute_hash()
                    if stored_hash != computed_hash:
                        raise ValueError(
                            f"Hash mismatch for record {record.record_id}: stored={stored_hash}, computed={computed_hash}"
                        )

                    self.records.append(record)
                    self.components.add(edge.from_component)
                    self.components.add(edge.to_component)

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    # Log corruption but continue
                    print(f"Warning: Failed to load record: {e}")
                    continue

    def _append_to_storage(self, record: DependencyRecord):
        """Append record to JSONL file (append-only)"""
        with open(self.storage_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict()) + "\n")

    def set_state(self, new_state: GraphState):
        """Transition state (INIT → RECORDING → VERIFICATION → LOCKED → SEALED)"""
        valid_transitions = {
            GraphState.INIT: [GraphState.RECORDING],
            GraphState.RECORDING: [GraphState.VERIFICATION],
            GraphState.VERIFICATION: [GraphState.LOCKED],
            GraphState.LOCKED: [GraphState.SEALED],
            GraphState.SEALED: [],  # No transitions from SEALED
        }

        if new_state not in valid_transitions.get(self.state, []):
            raise ValueError(
                f"Invalid state transition: {self.state.value} → {new_state.value}"
            )

        self.state = new_state

    def add_edge(
        self,
        from_component: str,
        to_component: str,
        relationship_type: DependencyType,
        verification_status: VerificationStatus = VerificationStatus.ASSUMED,
        evidence_link: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> DependencyRecord:
        """
        Add dependency edge (only in RECORDING state)

        C1 Scope Lock: No auto-inference
        C4 Data Protection: Append-only, immutable
        """
        if self.state != GraphState.RECORDING:
            raise ValueError(
                f"Cannot add edges in {self.state.value} state. Must be in RECORDING state."
            )

        edge = DependencyEdge(from_component, to_component, relationship_type)
        record = DependencyRecord(
            edge=edge,
            verification_status=verification_status,
            evidence_link=evidence_link,
            comment=comment,
        )

        self.records.append(record)
        self.components.add(from_component)
        self.components.add(to_component)
        self._append_to_storage(record)

        return record

    def verify_edge(
        self,
        record_id: str,
        verification_status: VerificationStatus,
        evidence_link: Optional[str] = None,
    ):
        """
        Verify edge (only in VERIFICATION state)

        C3 UNKNOWN Integrity: Creates new record, does not modify original
        """
        if self.state != GraphState.VERIFICATION:
            raise ValueError(
                f"Cannot verify edges in {self.state.value} state. Must be in VERIFICATION state."
            )

        # Find original record
        original = None
        for record in self.records:
            if record.record_id == record_id:
                original = record
                break

        if not original:
            raise ValueError(f"Record {record_id} not found")

        # Create new verification record (supersedes, doesn't modify)
        update_record = DependencyRecord(
            edge=original.edge,
            verification_status=verification_status,
            evidence_link=evidence_link,
            comment=f"Verification update for {record_id}",
        )
        update_record.record_id = record_id  # Link to original

        self.records.append(update_record)
        self._append_to_storage(update_record)

    def query_dependencies(
        self, component_id: str, direction: str = "outgoing"
    ) -> List[DependencyRecord]:
        """
        Query dependencies for a component

        Args:
            component_id: Component to query
            direction: "outgoing" (component → others) or "incoming" (others → component)

        Returns:
            List of dependency records
        """
        results = []
        for record in self.records:
            if direction == "outgoing" and record.edge.from_component == component_id:
                results.append(record)
            elif direction == "incoming" and record.edge.to_component == component_id:
                results.append(record)

        return results

    def detect_conflicts(self) -> List[ConflictRecord]:
        """
        Detect circular dependencies and other conflicts

        C2 Architecture Lock: Enforces acyclic graph property
        """
        conflicts = []

        # Build adjacency for cycle detection
        adj: Dict[str, List[str]] = {}
        for record in self.records:
            if record.verification_status == VerificationStatus.UNKNOWN:
                # UNKNOWN edges are included in conflict detection
                pass
            from_c = record.edge.from_component
            to_c = record.edge.to_component
            if from_c not in adj:
                adj[from_c] = []
            adj[from_c].append(to_c)

        # DFS to detect cycles
        def has_cycle(node: str, visited: Set[str], rec_stack: Set[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        visited = set()
        for component in self.components:
            if component not in visited:
                if has_cycle(component, visited, set()):
                    # Create conflict record
                    edge_ids = [
                        r.record_id
                        for r in self.records
                        if r.edge.from_component == component
                    ]
                    conflict = ConflictRecord(
                        edge_ids=edge_ids, conflict_type="circular_dependency"
                    )
                    conflicts.append(conflict)

        return conflicts

    def get_state(self) -> GraphState:
        """Get current state"""
        return self.state

    def get_components(self) -> Set[str]:
        """Get all components"""
        return self.components.copy()

    def get_records_count(self) -> int:
        """Get total records"""
        return len(self.records)

    def get_unknown_edges(self) -> List[DependencyRecord]:
        """Get all UNKNOWN edges (C3 UNKNOWN Integrity)"""
        return [
            r for r in self.records if r.verification_status == VerificationStatus.UNKNOWN
        ]
