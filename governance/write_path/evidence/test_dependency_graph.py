"""
HGD-UP-TEST-003-V3-2: Dependency Graph Test Suite

Phase 2 Tests:
- E3.1: Single-Level Dependency
- E3.2: Multi-Level Dependency
- Boundary tests for C1-C4

All tests verify Phase1 Design Specification compliance
"""

import pytest
import json
import hashlib
from pathlib import Path
from dependency_graph import (
    DependencyGraph,
    DependencyType,
    VerificationStatus,
    GraphState,
    DependencyEdge,
    DependencyRecord,
)


class TestE31SingleLevelDependency:
    """E3.1: Single-Level Dependency Test"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Create fresh graph for each test"""
        self.storage_path = Path(
            "governance/write_path/evidence/test_dependency_graph_e31.jsonl"
        )
        if self.storage_path.exists():
            self.storage_path.unlink()
        self.graph = DependencyGraph(storage_path=self.storage_path)

    def teardown_method(self):
        """Cleanup test files"""
        if self.storage_path.exists():
            self.storage_path.unlink()

    def test_e31_add_single_edge(self):
        """E3.1: Add single dependency edge A→B"""
        self.graph.set_state(GraphState.RECORDING)

        record = self.graph.add_edge(
            from_component="ComponentA",
            to_component="ComponentB",
            relationship_type=DependencyType.DEPENDS_ON,
            verification_status=VerificationStatus.VERIFIED,
            evidence_link="DC_20260824_001",
            comment="ComponentA depends on ComponentB API",
        )

        # Verify record was created
        assert record is not None
        assert record.edge.from_component == "ComponentA"
        assert record.edge.to_component == "ComponentB"
        assert record.verification_status == VerificationStatus.VERIFIED

        # Verify graph state
        assert self.graph.get_records_count() == 1
        assert "ComponentA" in self.graph.get_components()
        assert "ComponentB" in self.graph.get_components()

    def test_e31_immutability_on_reload(self):
        """E3.1: Verify record immutability across load/save cycles"""
        self.graph.set_state(GraphState.RECORDING)

        record1 = self.graph.add_edge(
            from_component="ServiceX",
            to_component="ServiceY",
            relationship_type=DependencyType.IMPACTS,
            verification_status=VerificationStatus.ASSUMED,
        )

        original_hash = record1.compute_hash()

        # Reload graph from storage
        graph2 = DependencyGraph(storage_path=self.storage_path)
        loaded_record = graph2.records[0]

        # Verify hash identical
        loaded_hash = loaded_record.compute_hash()
        assert original_hash == loaded_hash
        assert loaded_record.edge.from_component == "ServiceX"
        assert loaded_record.edge.to_component == "ServiceY"

    def test_e31_append_only_enforcement(self):
        """E3.1: Verify append-only property (no deletions)"""
        self.graph.set_state(GraphState.RECORDING)

        self.graph.add_edge(
            "A", "B", DependencyType.DEPENDS_ON, VerificationStatus.VERIFIED
        )
        self.graph.add_edge(
            "B", "C", DependencyType.IMPACTS, VerificationStatus.ASSUMED
        )

        # Try to access records - should return both
        assert self.graph.get_records_count() == 2

        # Attempt to "delete" by accessing storage directly should fail
        # (No delete method exists)
        assert not hasattr(self.graph, "delete_edge")


class TestE32MultiLevelDependency:
    """E3.2: Multi-Level Dependency Test"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Create fresh graph for each test"""
        self.storage_path = Path(
            "governance/write_path/evidence/test_dependency_graph_e32.jsonl"
        )
        if self.storage_path.exists():
            self.storage_path.unlink()
        self.graph = DependencyGraph(storage_path=self.storage_path)

    def teardown_method(self):
        """Cleanup test files"""
        if self.storage_path.exists():
            self.storage_path.unlink()

    def test_e32_chain_dependency_a_b_c_d(self):
        """E3.2: Build chain A→B→C→D and verify query"""
        self.graph.set_state(GraphState.RECORDING)

        # Create chain
        self.graph.add_edge("A", "B", DependencyType.DEPENDS_ON, VerificationStatus.VERIFIED)
        self.graph.add_edge("B", "C", DependencyType.DEPENDS_ON, VerificationStatus.VERIFIED)
        self.graph.add_edge("C", "D", DependencyType.DEPENDS_ON, VerificationStatus.VERIFIED)

        # Verify graph structure
        assert self.graph.get_records_count() == 3
        components = self.graph.get_components()
        assert all(c in components for c in ["A", "B", "C", "D"])

    def test_e32_query_outgoing_dependencies(self):
        """E3.2: Query outgoing dependencies for component"""
        self.graph.set_state(GraphState.RECORDING)

        # Create chain: A→B, A→C, B→D
        self.graph.add_edge("A", "B", DependencyType.DEPENDS_ON)
        self.graph.add_edge("A", "C", DependencyType.IMPACTS)
        self.graph.add_edge("B", "D", DependencyType.PROVIDES)

        # Query outgoing from A
        outgoing_a = self.graph.query_dependencies("A", direction="outgoing")
        assert len(outgoing_a) == 2
        targets = {r.edge.to_component for r in outgoing_a}
        assert targets == {"B", "C"}

        # Query outgoing from B
        outgoing_b = self.graph.query_dependencies("B", direction="outgoing")
        assert len(outgoing_b) == 1
        assert outgoing_b[0].edge.to_component == "D"

    def test_e32_query_incoming_dependencies(self):
        """E3.2: Query incoming dependencies for component"""
        self.graph.set_state(GraphState.RECORDING)

        # Create: A→B, C→B, B→D
        self.graph.add_edge("A", "B", DependencyType.DEPENDS_ON)
        self.graph.add_edge("C", "B", DependencyType.IMPACTS)
        self.graph.add_edge("B", "D", DependencyType.PROVIDES)

        # Query incoming to B
        incoming_b = self.graph.query_dependencies("B", direction="incoming")
        assert len(incoming_b) == 2
        sources = {r.edge.from_component for r in incoming_b}
        assert sources == {"A", "C"}

    def test_e32_circular_dependency_detection(self):
        """E3.2: Detect circular dependency A→B→A"""
        self.graph.set_state(GraphState.RECORDING)

        self.graph.add_edge("A", "B", DependencyType.DEPENDS_ON)
        self.graph.add_edge("B", "A", DependencyType.IMPACTS)

        # Detect conflicts
        conflicts = self.graph.detect_conflicts()
        assert len(conflicts) > 0
        assert conflicts[0].conflict_type == "circular_dependency"


class TestC1ScopeLock:
    """C1: Scope Lock - Verify no scope expansion"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Create fresh graph for each test"""
        self.storage_path = Path(
            "governance/write_path/evidence/test_dependency_graph_c1.jsonl"
        )
        if self.storage_path.exists():
            self.storage_path.unlink()
        self.graph = DependencyGraph(storage_path=self.storage_path)

    def teardown_method(self):
        if self.storage_path.exists():
            self.storage_path.unlink()

    def test_c1_no_auto_inference_method_exists(self):
        """C1: Verify no auto-inference method exists"""
        # Should NOT have methods like:
        # - auto_infer_dependencies()
        # - infer_from_code_analysis()
        # - predict_dependencies()
        assert not hasattr(self.graph, "auto_infer_dependencies")
        assert not hasattr(self.graph, "infer_from_code_analysis")
        assert not hasattr(self.graph, "predict_dependencies")

    def test_c1_api_methods_match_spec(self):
        """C1: Verify API methods match Phase1 spec exactly"""
        required_methods = [
            "add_edge",
            "verify_edge",
            "query_dependencies",
            "detect_conflicts",
        ]
        for method in required_methods:
            assert hasattr(self.graph, method), f"Missing required method: {method}"


class TestC3UnknownIntegrity:
    """C3: UNKNOWN Integrity Protection"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.storage_path = Path(
            "governance/write_path/evidence/test_dependency_graph_c3.jsonl"
        )
        if self.storage_path.exists():
            self.storage_path.unlink()
        self.graph = DependencyGraph(storage_path=self.storage_path)

    def teardown_method(self):
        if self.storage_path.exists():
            self.storage_path.unlink()

    def test_c3_unknown_edges_preserved(self):
        """C3: UNKNOWN edges are recorded and preserved"""
        self.graph.set_state(GraphState.RECORDING)

        # Add UNKNOWN edge
        record = self.graph.add_edge(
            "ComponentX",
            "ComponentY",
            DependencyType.DEPENDS_ON,
            verification_status=VerificationStatus.UNKNOWN,
            comment="Runtime dependency, not statically verifiable",
        )

        # Verify UNKNOWN status preserved
        assert record.verification_status == VerificationStatus.UNKNOWN

        # Query UNKNOWN edges
        unknown_edges = self.graph.get_unknown_edges()
        assert len(unknown_edges) == 1
        assert unknown_edges[0].record_id == record.record_id

    def test_c3_unknown_cannot_be_deleted(self):
        """C3: UNKNOWN edges cannot be deleted (append-only)"""
        self.graph.set_state(GraphState.RECORDING)

        self.graph.add_edge(
            "A", "B", DependencyType.DEPENDS_ON, VerificationStatus.UNKNOWN
        )

        # Verify no delete method
        assert not hasattr(self.graph, "delete_edge")
        assert not hasattr(self.graph, "remove_edge")

        # Verify record still exists
        unknown = self.graph.get_unknown_edges()
        assert len(unknown) == 1


class TestC4DataProtection:
    """C4: Data Protection - Immutability and audit trail"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.storage_path = Path(
            "governance/write_path/evidence/test_dependency_graph_c4.jsonl"
        )
        if self.storage_path.exists():
            self.storage_path.unlink()
        self.graph = DependencyGraph(storage_path=self.storage_path)

    def teardown_method(self):
        if self.storage_path.exists():
            self.storage_path.unlink()

    def test_c4_hash_integrity_verification(self):
        """C4: Each record has SHA256 hash for integrity"""
        self.graph.set_state(GraphState.RECORDING)

        record = self.graph.add_edge(
            "A", "B", DependencyType.DEPENDS_ON, VerificationStatus.VERIFIED
        )

        # Verify hash exists and is SHA256 format
        record_hash = record.compute_hash()
        assert len(record_hash) == 64  # SHA256 hex digest length
        assert all(c in "0123456789abcdef" for c in record_hash)

    def test_c4_no_update_or_delete_operations(self):
        """C4: No destructive operations (update/delete)"""
        # Should not have:
        assert not hasattr(self.graph, "delete_record")
        assert not hasattr(self.graph, "update_record")
        assert not hasattr(self.graph, "delete_edge")
        assert not hasattr(self.graph, "modify_edge")

    def test_c4_append_only_file_format(self):
        """C4: Storage is append-only JSONL"""
        self.graph.set_state(GraphState.RECORDING)

        self.graph.add_edge("A", "B", DependencyType.DEPENDS_ON)
        self.graph.add_edge("C", "D", DependencyType.IMPACTS)

        # Verify JSONL format
        with open(self.storage_path, "r") as f:
            lines = f.readlines()
            assert len(lines) == 2
            for line in lines:
                data = json.loads(line)
                assert "record_id" in data
                assert "hash" in data
                assert "edge" in data


class TestStateTransitions:
    """Test state machine transitions"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.storage_path = Path(
            "governance/write_path/evidence/test_dependency_graph_state.jsonl"
        )
        if self.storage_path.exists():
            self.storage_path.unlink()
        self.graph = DependencyGraph(storage_path=self.storage_path)

    def teardown_method(self):
        if self.storage_path.exists():
            self.storage_path.unlink()

    def test_state_init_to_recording(self):
        """Test INIT → RECORDING transition"""
        assert self.graph.state == GraphState.INIT
        self.graph.set_state(GraphState.RECORDING)
        assert self.graph.state == GraphState.RECORDING

    def test_state_recording_to_verification(self):
        """Test RECORDING → VERIFICATION transition"""
        self.graph.set_state(GraphState.RECORDING)
        self.graph.set_state(GraphState.VERIFICATION)
        assert self.graph.state == GraphState.VERIFICATION

    def test_invalid_state_transition(self):
        """Test invalid state transition raises error"""
        self.graph.set_state(GraphState.RECORDING)

        with pytest.raises(ValueError):
            self.graph.set_state(GraphState.LOCKED)  # Invalid: RECORDING → LOCKED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
