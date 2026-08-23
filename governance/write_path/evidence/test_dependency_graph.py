"""
Phase 2: Dependency Graph Testing
UP-TEST-003 V3.2 Evidence State Machine Extension - E3.1 and E3.2 Test Scenarios

Test scenarios from Phase 1 Design Specification:
- E3.1: Single-level dependency tracking
- E3.2: Multi-level dependency tracking (depth 1-3)
"""

from dependency_graph import DependencyGraphStore, get_store


class AssertionError(Exception):
    """Custom assertion for standalone testing."""
    pass


class TestE31SingleLevelDependency:
    """
    E3.1: Single-Level Dependency (Depth 1)

    Test Setup:
    - Evidence EVI-001 is UNKNOWN
    - Evidence EVI-001 has blocking dependency on EVI-002
    - Evidence EVI-002 is VERIFIED

    Expected Result:
    - Can identify immediate dependencies
    - Dependency chain length = 1
    """

    def test_e31_basic_dependency_tracking(self):
        """Test E3.1: Single-level dependency."""
        store = DependencyGraphStore()

        # Setup: Create dependency edge
        # EVI-001 depends on EVI-002 (blocked by EVI-002)
        edge = store.add_edge(
            dependency_id="DEP-001",
            source_evidence="EVI-001",
            target_evidence="EVI-002",
            created_by="test_runner",
            status="OPEN"
        )

        # Verify edge created
        assert edge["dependency_id"] == "DEP-001"
        assert edge["source_evidence"] == "EVI-001"
        assert edge["target_evidence"] == "EVI-002"
        assert edge["status"] == "OPEN"

        # Test: Query blocking chain for EVI-001
        blocking_chain = store.get_blocking_chain("EVI-001")

        # Expected Result
        assert blocking_chain == ["EVI-002"], f"Expected ['EVI-002'], got {blocking_chain}"
        assert len(blocking_chain) == 1, f"Expected length 1, got {len(blocking_chain)}"

        # Pass Criteria
        print("E3.1 PASS: Can identify immediate dependencies")
        print("E3.1 PASS: Dependency chain length = 1")

    def test_e31_open_dependencies_field(self):
        """Test E3.1: open_dependencies field population."""
        store = DependencyGraphStore()

        # Setup: Create dependency for EVI-001
        store.add_edge(
            dependency_id="DEP-001",
            source_evidence="EVI-001",
            target_evidence="EVI-002",
            created_by="test_runner"
        )

        # Test: Get open dependencies (for EvidenceRecord.open_dependencies field)
        open_deps = store.get_open_dependencies("EVI-001")

        # Expected Result
        assert "DEP-001" in open_deps
        assert len(open_deps) == 1

        print("E3.1 PASS: open_dependencies field correctly populated")


class TestE32MultiLevelDependency:
    """
    E3.2: Multi-Level Dependency (Depth 1-3)

    Test Setup:
    - Chain: EVI-001 -> EVI-002 -> EVI-003 -> EVI-004
    - DEP-001: EVI-001 blocked by EVI-002 (OPEN)
    - DEP-002: EVI-002 blocked by EVI-003 (OPEN)
    - DEP-003: EVI-003 blocked by EVI-004 (OPEN)

    Expected Result:
    - Can traverse depth 1 (immediate)
    - Can traverse depth 2 (transitive)
    - Can traverse depth 3 (deep transitive)
    - Full chain reconstructible
    """

    def test_e32_multi_level_dependency_chain(self):
        """Test E3.2: Multi-level dependency chain."""
        store = DependencyGraphStore()

        # Setup: Create dependency chain EVI-001 -> EVI-002 -> EVI-003 -> EVI-004
        store.add_edge(
            dependency_id="DEP-001",
            source_evidence="EVI-001",
            target_evidence="EVI-002",
            created_by="test_runner"
        )

        store.add_edge(
            dependency_id="DEP-002",
            source_evidence="EVI-002",
            target_evidence="EVI-003",
            created_by="test_runner"
        )

        store.add_edge(
            dependency_id="DEP-003",
            source_evidence="EVI-003",
            target_evidence="EVI-004",
            created_by="test_runner"
        )

        # Test: Full blocking chain for EVI-001
        blocking_chain = store.get_blocking_chain("EVI-001", max_depth=3)

        # Expected Result
        assert blocking_chain == ["EVI-002", "EVI-003", "EVI-004"], \
            f"Expected ['EVI-002', 'EVI-003', 'EVI-004'], got {blocking_chain}"
        assert len(blocking_chain) == 3

        print("E3.2 PASS: Full chain reconstructible")

    def test_e32_depth_specific_dependencies(self):
        """Test E3.2: Dependencies at specific depth levels."""
        store = DependencyGraphStore()

        # Setup: Same chain as test_e32_multi_level_dependency_chain
        store.add_edge(
            dependency_id="DEP-001",
            source_evidence="EVI-001",
            target_evidence="EVI-002",
            created_by="test_runner"
        )

        store.add_edge(
            dependency_id="DEP-002",
            source_evidence="EVI-002",
            target_evidence="EVI-003",
            created_by="test_runner"
        )

        store.add_edge(
            dependency_id="DEP-003",
            source_evidence="EVI-003",
            target_evidence="EVI-004",
            created_by="test_runner"
        )

        # Test: Dependencies at each level
        level_1 = store.get_dependencies("EVI-001", depth=1)
        level_2 = store.get_dependencies("EVI-001", depth=2)
        level_3 = store.get_dependencies("EVI-001", depth=3)

        # Expected Result
        assert level_1 == ["EVI-002"], f"Expected ['EVI-002'] at depth 1, got {level_1}"
        assert level_2 == ["EVI-003"], f"Expected ['EVI-003'] at depth 2, got {level_2}"
        assert level_3 == ["EVI-004"], f"Expected ['EVI-004'] at depth 3, got {level_3}"

        # Pass Criteria
        print("E3.2 PASS: Can traverse depth 1 (immediate)")
        print("E3.2 PASS: Can traverse depth 2 (transitive)")
        print("E3.2 PASS: Can traverse depth 3 (deep transitive)")

    def test_e32_no_edge_loss(self):
        """Test E3.2: No loss of edges at any depth."""
        store = DependencyGraphStore()

        # Setup: Create all edges
        edges_created = []
        store.add_edge("DEP-001", "EVI-001", "EVI-002", created_by="test")
        edges_created.append("DEP-001")
        store.add_edge("DEP-002", "EVI-002", "EVI-003", created_by="test")
        edges_created.append("DEP-002")
        store.add_edge("DEP-003", "EVI-003", "EVI-004", created_by="test")
        edges_created.append("DEP-003")

        # Test: Verify all edges exist
        all_edges = store.get_all_edges()
        all_edge_ids = [e["dependency_id"] for e in all_edges]

        # Expected Result
        assert len(all_edges) == 3
        for edge_id in edges_created:
            assert edge_id in all_edge_ids, f"Edge {edge_id} lost"

        print("E3.2 PASS: No loss of edges at any depth")


class TestDependencyGraphEdgeCases:
    """Test edge cases and error conditions."""

    def test_duplicate_edge_prevention(self):
        """Test that duplicate dependency IDs are prevented."""
        store = DependencyGraphStore()

        store.add_edge("DEP-001", "EVI-001", "EVI-002")

        # Attempt to add duplicate
        try:
            store.add_edge("DEP-001", "EVI-003", "EVI-004")
            raise AssertionError("Expected ValueError for duplicate edge")
        except ValueError as e:
            if "already exists" not in str(e):
                raise AssertionError(f"Wrong error message: {e}")

        print("Duplicate edge prevention: PASS")

    def test_resolved_edge_not_in_chain(self):
        """Test that RESOLVED edges are excluded from blocking chains."""
        store = DependencyGraphStore()

        # Add two edges
        store.add_edge("DEP-001", "EVI-001", "EVI-002")
        store.add_edge("DEP-002", "EVI-002", "EVI-003")

        # Resolve first edge
        store.resolve_edge("DEP-001")

        # Check blocking chain excludes resolved edge
        blocking_chain = store.get_blocking_chain("EVI-001")

        # DEP-001 is resolved, so it shouldn't contribute EVI-002 to the chain
        # However, DEP-002 creates chain from EVI-002 to EVI-003
        # Since DEP-001 is resolved, EVI-002 is no longer blocked,
        # so we shouldn't traverse through it
        assert blocking_chain == [], f"Expected empty chain after resolving DEP-001, got {blocking_chain}"

    def test_remove_edge(self):
        """Test edge removal."""
        store = DependencyGraphStore()

        store.add_edge("DEP-001", "EVI-001", "EVI-002")
        assert store.get_edge("DEP-001") is not None

        # Remove edge
        removed = store.remove_edge("DEP-001")
        assert removed is True

        # Verify removal
        assert store.get_edge("DEP-001") is None

        # Verify blocking chain is now empty
        blocking_chain = store.get_blocking_chain("EVI-001")
        assert blocking_chain == []

    def test_store_statistics(self):
        """Test store statistics tracking."""
        store = DependencyGraphStore()

        # Add some edges
        store.add_edge("DEP-001", "EVI-001", "EVI-002")
        store.add_edge("DEP-002", "EVI-001", "EVI-003")
        store.add_edge("DEP-003", "EVI-002", "EVI-004")

        # Resolve one
        store.resolve_edge("DEP-001")

        stats = store.stats()

        assert stats["total_edges"] == 3
        assert stats["open_edges"] == 2
        assert stats["resolved_edges"] == 1

    def test_nonexistent_evidence_no_error(self):
        """Test that querying nonexistent evidence returns empty result."""
        store = DependencyGraphStore()

        # Query evidence that doesn't exist
        blocking_chain = store.get_blocking_chain("EVI-NONEXISTENT")

        assert blocking_chain == []
        assert len(blocking_chain) == 0


def run_e31_tests():
    """Run all E3.1 tests."""
    print("\n" + "="*60)
    print("PHASE 2 - E3.1: Single-Level Dependency Testing")
    print("="*60)

    test_class = TestE31SingleLevelDependency()
    test_class.test_e31_basic_dependency_tracking()
    test_class.test_e31_open_dependencies_field()

    print("\nE3.1: ALL TESTS PASSED")


def run_e32_tests():
    """Run all E3.2 tests."""
    print("\n" + "="*60)
    print("PHASE 2 - E3.2: Multi-Level Dependency Testing")
    print("="*60)

    test_class = TestE32MultiLevelDependency()
    test_class.test_e32_multi_level_dependency_chain()
    test_class.test_e32_depth_specific_dependencies()
    test_class.test_e32_no_edge_loss()

    print("\nE3.2: ALL TESTS PASSED")


def run_all_tests():
    """Run all Phase 2 tests."""
    print("\n" + "="*80)
    print("PHASE 2: DEPENDENCY GRAPH IMPLEMENTATION")
    print("UP-TEST-003 V3.2 Evidence State Machine Extension")
    print("="*80)

    run_e31_tests()
    run_e32_tests()

    # Run edge case tests
    print("\n" + "="*60)
    print("PHASE 2: Edge Case Testing")
    print("="*60)

    edge_case_tests = TestDependencyGraphEdgeCases()
    edge_case_tests.test_duplicate_edge_prevention()
    edge_case_tests.test_resolved_edge_not_in_chain()
    edge_case_tests.test_remove_edge()
    edge_case_tests.test_store_statistics()
    edge_case_tests.test_nonexistent_evidence_no_error()

    print("\nEdge Case Tests: ALL PASSED")

    print("\n" + "="*80)
    print("PHASE 2: ALL TESTS PASSED")
    print("Status: PHASE 2 COMPLETE - Ready for Code Review")
    print("="*80)


if __name__ == "__main__":
    run_all_tests()
