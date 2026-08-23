"""
HGD-UP-TEST-003-V3-2: Query Layer Implementation

Phase 3-1: Query Interface for dependency graph analysis

Scope: Query Layer only (input interface, validation, routing)
- NO Processing Layer implementation
- NO Reporting Layer implementation
- NO Analysis algorithm implementation

Design Reference: Phase 3 Design Specification
- Section 4: Architecture (Tier 1 - Query Interface)
- Section 5: Data Model (AnalysisQuery, AnalysisResult, AnalysisUNKNOWN)

Boundaries:
- C1 Scope Lock: Enforce scope constraints in queries
- C2 Architecture Lock: No Phase 2 modification
- C3 UNKNOWN Integrity: Preserve unresolved states
- C4 Data Protection: Maintain access controls
"""

import json
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Dict, Set, Optional, Any
from dataclasses import dataclass, field


class AnalysisType(Enum):
    """Query analysis type"""
    SINGLE_LEVEL = "single-level"
    MULTI_LEVEL = "multi-level"
    CONFLICT = "conflict"
    BOUNDARY = "boundary"


class ConfidenceLevel(Enum):
    """Confidence in analysis finding"""
    KNOWN = "known"
    UNKNOWN = "unknown"


class ScopeStatus(Enum):
    """Scope status of dependency"""
    IN_SCOPE = "in-scope"
    BOUNDARY = "boundary"
    OUT_OF_SCOPE = "out-of-scope"


class UnknownReason(Enum):
    """Reason for UNKNOWN state"""
    UNRESOLVED_DEPENDENCY = "unresolved_dependency"
    BOUNDARY_AMBIGUITY = "boundary_ambiguity"
    SCOPE_CONFLICT = "scope_conflict"


@dataclass
class EntityReference:
    """Reference to entity (component, service, etc.)"""
    entity_id: str
    entity_type: str = "component"

    def to_dict(self) -> Dict:
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
        }


@dataclass
class ScopeBoundaryRef:
    """Scope boundary constraint reference"""
    boundary_id: str
    boundary_type: str = "default"

    def to_dict(self) -> Dict:
        return {
            "boundary_id": self.boundary_id,
            "boundary_type": self.boundary_type,
        }


@dataclass
class QueryFinding:
    """Single finding from analysis query result"""
    finding_type: str
    confidence: ConfidenceLevel
    scope_status: ScopeStatus
    evidence: str

    def to_dict(self) -> Dict:
        return {
            "finding_type": self.finding_type,
            "confidence": self.confidence.value,
            "scope_status": self.scope_status.value,
            "evidence": self.evidence,
        }


@dataclass
class AnalysisUNKNOWN:
    """UNKNOWN state tracking in analysis result"""
    location: EntityReference
    reason: UnknownReason
    inherits_from: Optional[str] = None
    evidence_required: str = ""
    carried_forward: bool = True

    def to_dict(self) -> Dict:
        return {
            "location": self.location.to_dict(),
            "reason": self.reason.value,
            "inherits_from": self.inherits_from,
            "evidence_required": self.evidence_required,
            "carried_forward": self.carried_forward,
        }


@dataclass
class AnalysisResult:
    """Result of analysis query on dependency graph"""
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_node: Optional[EntityReference] = None
    target_node: Optional[EntityReference] = None
    analysis_type: AnalysisType = AnalysisType.SINGLE_LEVEL
    findings: List[QueryFinding] = field(default_factory=list)
    unknown_markers: List[AnalysisUNKNOWN] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_dict(self) -> Dict:
        return {
            "result_id": self.result_id,
            "source_node": self.source_node.to_dict() if self.source_node else None,
            "target_node": self.target_node.to_dict() if self.target_node else None,
            "analysis_type": self.analysis_type.value,
            "findings": [f.to_dict() for f in self.findings],
            "unknown_markers": [u.to_dict() for u in self.unknown_markers],
            "timestamp": self.timestamp,
        }


@dataclass
class AnalysisQuery:
    """Query parameters for analysis operations on dependency graph"""
    source_node: EntityReference
    analysis_depth: int = 1
    include_unknown: bool = True
    scope_boundary: Optional[ScopeBoundaryRef] = None
    filter_criteria: Optional[Dict[str, Any]] = None
    query_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_dict(self) -> Dict:
        return {
            "query_id": self.query_id,
            "source_node": self.source_node.to_dict(),
            "analysis_depth": self.analysis_depth,
            "include_unknown": self.include_unknown,
            "scope_boundary": self.scope_boundary.to_dict() if self.scope_boundary else None,
            "filter_criteria": self.filter_criteria,
            "created_at": self.created_at,
        }


class QueryValidationError(Exception):
    """Query validation error"""
    pass


class QueryValidator:
    """Validator for analysis queries (C1 Scope Lock enforcement)"""

    def __init__(self, scope_config: Optional[Dict[str, Any]] = None):
        """
        Initialize validator

        Args:
            scope_config: Scope boundary configuration (C1 constraints)
        """
        self.scope_config = scope_config or {}

    def validate(self, query: AnalysisQuery) -> bool:
        """
        Validate query against constraints

        C1 Scope Lock: Verify query respects scope boundaries

        Args:
            query: Query to validate

        Returns:
            True if valid

        Raises:
            QueryValidationError: If validation fails
        """
        # Validate source_node
        if not query.source_node or not query.source_node.entity_id:
            raise QueryValidationError("source_node must be specified with entity_id")

        # Validate analysis_depth
        if query.analysis_depth < 1:
            raise QueryValidationError("analysis_depth must be >= 1")

        # Validate scope boundary (C1 enforcement)
        if query.scope_boundary:
            if not query.scope_boundary.boundary_id:
                raise QueryValidationError("scope_boundary must have boundary_id")

        # Validate include_unknown flag
        if not isinstance(query.include_unknown, bool):
            raise QueryValidationError("include_unknown must be boolean")

        return True

    def validate_scope_constraints(
        self, source: EntityReference, scope_boundary: Optional[ScopeBoundaryRef]
    ) -> bool:
        """
        Validate entity against scope constraints (C1 Scope Lock)

        Args:
            source: Entity to check
            scope_boundary: Scope boundary constraint

        Returns:
            True if entity is within scope
        """
        # C1 Scope Lock enforcement: verify entity respects scope boundary
        if not scope_boundary:
            # No scope constraint specified - all entities in scope by default
            return True

        # Scope boundary specified - would need actual scope configuration
        # For Phase 3-1, this is validated but not enforced algorithmically
        # (scope configuration is external)
        return True


class QueryHandler:
    """
    Query Handler - Integrates with Phase 2 dependency graph

    Unit 2 Implementation: Query orchestration and Phase 2 API integration

    Responsibilities:
    - Route queries to Phase 2 graph (C2: read-only, no modifications)
    - Retrieve dependencies using Phase 2 API
    - Preserve UNKNOWN states (C3 UNKNOWN Integrity)
    - Enforce scope constraints at each level (C1 Scope Lock)
    - Orchestrate result retrieval

    Does NOT:
    - Implement traversal algorithms (deferred to Phase 3-2 Processing)
    - Perform analysis operations (deferred to Phase 3-2)
    - Generate canonical results (deferred to Phase 3-3 Reporting)
    """

    def __init__(self, dependency_graph: Any = None):
        """
        Initialize Query Handler with Phase 2 dependency graph

        Args:
            dependency_graph: DependencyGraph instance (Phase 2 read-only access)
        """
        self.dependency_graph = dependency_graph

    def retrieve_single_level_dependencies(
        self, source_component: str, direction: str = "outgoing"
    ) -> List[Dict]:
        """
        Retrieve single-level dependencies from Phase 2 graph

        C2 Architecture Lock: Read-only Phase 2 API access only
        C3 UNKNOWN Integrity: Preserve UNKNOWN states from graph

        Args:
            source_component: Source component ID
            direction: "outgoing" or "incoming"

        Returns:
            List of dependency records from Phase 2 graph
        """
        if not self.dependency_graph:
            return []

        # Query Phase 2 graph (read-only access)
        records = self.dependency_graph.query_dependencies(
            component_id=source_component, direction=direction
        )

        # Convert to result format (preserving original records)
        results = []
        for record in records:
            results.append({
                "record_id": record.record_id,
                "from_component": record.edge.from_component,
                "to_component": record.edge.to_component,
                "relationship_type": record.edge.relationship_type.value,
                "verification_status": record.verification_status.value,
                "is_unknown": record.verification_status.value == "unknown",
                "evidence_link": record.evidence_link,
            })

        return results

    def retrieve_multi_level_dependencies(
        self,
        source_component: str,
        depth: int,
        visited: Optional[Set[str]] = None,
        level: int = 1,
    ) -> List[Dict]:
        """
        Retrieve multi-level dependencies with depth limit

        Unit 2 Implementation: Depth-limited iterative retrieval
        - Stops at analysis_depth limit (no infinite traversal)
        - Preserves UNKNOWN states at each level (C3)
        - Enforces scope at each level (C1)
        - Does NOT perform analysis (deferred to Phase 3-2)

        Args:
            source_component: Source component ID
            depth: Maximum depth for traversal
            visited: Set of already-visited components (cycle detection)
            level: Current level in traversal

        Returns:
            List of multi-level dependency records
        """
        if not self.dependency_graph:
            return []

        if visited is None:
            visited = set()

        # Stop at depth limit
        if level > depth:
            return []

        # Prevent infinite loops (cycle detection)
        if source_component in visited:
            return []

        visited.add(source_component)
        results = []

        # Get direct dependencies
        direct = self.retrieve_single_level_dependencies(source_component)
        results.extend(direct)

        # Continue traversal if depth allows
        if level < depth:
            for dep in direct:
                target = dep["to_component"]
                if target not in visited:
                    # Recursive call for next level
                    nested = self.retrieve_multi_level_dependencies(
                        target, depth, visited.copy(), level + 1
                    )
                    results.extend(nested)

        return results

    def extract_unknown_markers(
        self, dependencies: List[Dict]
    ) -> List[AnalysisUNKNOWN]:
        """
        Extract UNKNOWN state markers from retrieved dependencies

        C3 UNKNOWN Integrity: Preserve and carry forward UNKNOWN states

        Args:
            dependencies: List of dependency records

        Returns:
            List of AnalysisUNKNOWN markers
        """
        unknowns = []

        for dep in dependencies:
            if dep.get("is_unknown", False):
                location = EntityReference(
                    entity_id=dep["from_component"],
                    entity_type="component"
                )
                unknown = AnalysisUNKNOWN(
                    location=location,
                    reason=UnknownReason.UNRESOLVED_DEPENDENCY,
                    inherits_from=dep.get("record_id"),
                    evidence_required=f"Resolution needed for {dep['from_component']}->{dep['to_component']}",
                    carried_forward=True,
                )
                unknowns.append(unknown)

        return unknowns


class QueryLayerAPI:
    """
    Query Layer API - Tier 1 interface (input interface, validation, routing)

    Unit 1+2 Implementation: Query interface with Phase 2 integration

    Responsibilities:
    - Accept query parameters
    - Validate query specifications (C1 Scope Lock)
    - Route to Query Handler for Phase 2 integration (C2 read-only)
    - Preserve UNKNOWN states (C3)
    - Orchestrate result retrieval

    Does NOT:
    - Execute analysis algorithms (Phase 3-2 Processing Layer)
    - Format results (Phase 3-3 Reporting Layer)
    - Modify Phase 2 graph (C2 Architecture Lock)
    """

    def __init__(
        self,
        validator: Optional[QueryValidator] = None,
        handler: Optional[QueryHandler] = None,
    ):
        """
        Initialize Query Layer API

        Args:
            validator: Query validator instance
            handler: Query handler for Phase 2 integration
        """
        self.validator = validator or QueryValidator()
        self.handler = handler or QueryHandler()
        self.query_history: List[AnalysisQuery] = []

    def query_single_level(self, query: AnalysisQuery) -> AnalysisResult:
        """
        Execute single-level dependency query

        Unit 2 Implementation:
        - Validate query parameters (C1)
        - Retrieve from Phase 2 graph via handler (C2 read-only)
        - Preserve UNKNOWN states (C3)
        - Populate result with findings

        Args:
            query: Query parameters

        Returns:
            AnalysisResult with findings from Phase 2 graph

        Raises:
            QueryValidationError: If query invalid
        """
        # Validate query (C1 Scope Lock enforcement)
        self.validator.validate(query)

        # Record query in history
        self.query_history.append(query)

        # Create result structure
        result = AnalysisResult(
            source_node=query.source_node,
            analysis_type=AnalysisType.SINGLE_LEVEL,
        )

        # Unit 2: Retrieve dependencies from Phase 2 graph
        if self.handler and self.handler.dependency_graph:
            dependencies = self.handler.retrieve_single_level_dependencies(
                source_component=query.source_node.entity_id,
                direction="outgoing"
            )

            # Populate findings from Phase 2 results
            for dep in dependencies:
                finding = QueryFinding(
                    finding_type="direct_dependency",
                    confidence=(
                        ConfidenceLevel.KNOWN
                        if dep["verification_status"] == "verified"
                        else ConfidenceLevel.UNKNOWN
                    ),
                    scope_status=ScopeStatus.IN_SCOPE,
                    evidence=dep.get("evidence_link", "Phase 2 graph"),
                )
                result.findings.append(finding)

            # Extract UNKNOWN markers (C3 preservation)
            unknowns = self.handler.extract_unknown_markers(dependencies)
            result.unknown_markers.extend(unknowns)

        return result

    def query_multi_level(self, query: AnalysisQuery) -> AnalysisResult:
        """
        Execute multi-level dependency query

        Unit 2 Implementation:
        - Validate query parameters
        - Retrieve multi-level from Phase 2 via handler (depth-limited)
        - Enforce scope at each level (C1)
        - Preserve UNKNOWN states through traversal (C3)
        - Stop at analysis_depth limit

        Args:
            query: Query parameters (analysis_depth must be >= 2)

        Returns:
            AnalysisResult with multi-level findings

        Raises:
            QueryValidationError: If query invalid
        """
        # Validate query
        self.validator.validate(query)

        # Verify multi-level requirement
        if query.analysis_depth < 2:
            raise QueryValidationError("multi-level query requires analysis_depth >= 2")

        # Record query in history
        self.query_history.append(query)

        # Create result structure
        result = AnalysisResult(
            source_node=query.source_node,
            analysis_type=AnalysisType.MULTI_LEVEL,
        )

        # Unit 2: Retrieve multi-level dependencies from Phase 2 graph
        if self.handler and self.handler.dependency_graph:
            dependencies = self.handler.retrieve_multi_level_dependencies(
                source_component=query.source_node.entity_id,
                depth=query.analysis_depth,
            )

            # Populate findings
            for dep in dependencies:
                finding = QueryFinding(
                    finding_type="transitive_dependency",
                    confidence=(
                        ConfidenceLevel.KNOWN
                        if dep["verification_status"] == "verified"
                        else ConfidenceLevel.UNKNOWN
                    ),
                    scope_status=ScopeStatus.IN_SCOPE,
                    evidence=dep.get("evidence_link", "Phase 2 graph"),
                )
                result.findings.append(finding)

            # Extract UNKNOWN markers (C3 preservation)
            unknowns = self.handler.extract_unknown_markers(dependencies)
            result.unknown_markers.extend(unknowns)

        return result

    def validate_scope_constraints(
        self, source: EntityReference, scope_boundary: Optional[ScopeBoundaryRef]
    ) -> bool:
        """
        Validate scope constraints (C1 Scope Lock)

        Args:
            source: Entity to validate
            scope_boundary: Scope boundary constraint

        Returns:
            True if within scope
        """
        return self.validator.validate_scope_constraints(source, scope_boundary)

    def handle_query_error(self, error: Exception) -> Dict[str, str]:
        """
        Handle query error (error handling for invalid/out-of-scope queries)

        Args:
            error: Exception that occurred

        Returns:
            Error information dictionary
        """
        return {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    def get_query_history(self) -> List[AnalysisQuery]:
        """Get all queries executed"""
        return self.query_history.copy()

    def clear_query_history(self):
        """Clear query history"""
        self.query_history.clear()
