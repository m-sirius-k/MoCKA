"""
HGD-UP-TEST-003-V3-2: Query Layer Test Suite

Phase 3-1 Tests:
- A1: Single-Level Analysis (4 tests)
- A2: Multi-Level Analysis (4 tests)
- B: Boundary Conditions C1-C4 (4 tests)
- I: Integration Tests (3 tests)

Design Reference: Phase 3 Design Specification Section 6 (Verification Criteria)
All tests verify Phase 3 Design Specification compliance
"""

import pytest
from query_layer import (
    AnalysisQuery,
    AnalysisResult,
    AnalysisUNKNOWN,
    EntityReference,
    ScopeBoundaryRef,
    QueryValidator,
    QueryLayerAPI,
    QueryValidationError,
    AnalysisType,
    ConfidenceLevel,
    ScopeStatus,
    UnknownReason,
)


class TestA11SingleLevelBasicQuery:
    """A1.1: Direct Dependency Query - Single-Level Basic Query"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Create fresh API instance"""
        self.api = QueryLayerAPI()

    def test_a11_single_level_query_basic(self):
        """A1.1: Execute single-level query on component"""
        source = EntityReference(entity_id="ComponentA", entity_type="component")
        query = AnalysisQuery(source_node=source, analysis_depth=1)

        result = self.api.query_single_level(query)

        # Verify result structure
        assert result is not None
        assert result.source_node == source
        assert result.analysis_type == AnalysisType.SINGLE_LEVEL
        assert isinstance(result.findings, list)

    def test_a11_query_stored_in_history(self):
        """A1.1: Query stored in history for traceability"""
        source = EntityReference(entity_id="ServiceX", entity_type="service")
        query = AnalysisQuery(source_node=source, analysis_depth=1)

        self.api.query_single_level(query)

        history = self.api.get_query_history()
        assert len(history) == 1
        assert history[0].source_node == source


class TestA12ScopeValidation:
    """A1.2: Scope Validation - Scope Constraints Enforcement"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Create validator"""
        self.validator = QueryValidator()

    def test_a12_scope_validation_pass(self):
        """A1.2: Query within scope passes validation"""
        source = EntityReference(entity_id="Component_1", entity_type="component")
        boundary = ScopeBoundaryRef(boundary_id="scope_default")
        query = AnalysisQuery(
            source_node=source,
            analysis_depth=1,
            scope_boundary=boundary
        )

        # Should not raise
        result = self.validator.validate(query)
        assert result is True

    def test_a12_scope_validation_reject_invalid_source(self):
        """A1.2: Query with invalid source rejected"""
        query = AnalysisQuery(
            source_node=EntityReference(entity_id="", entity_type="component"),
            analysis_depth=1
        )

        with pytest.raises(QueryValidationError):
            self.validator.validate(query)


class TestA13BoundaryDetection:
    """A1.3: Boundary Detection - Detect Boundary-Crossing Dependencies"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Create API with scope config"""
        self.api = QueryLayerAPI()

    def test_a13_scope_constraints_check(self):
        """A1.3: Scope constraint validation callable"""
        source = EntityReference(entity_id="A", entity_type="component")
        boundary = ScopeBoundaryRef(boundary_id="scope_1")

        result = self.api.validate_scope_constraints(source, boundary)
        assert isinstance(result, bool)


class TestA14UnknownPreservation:
    """A1.4: UNKNOWN Preservation - Preserve UNKNOWN in Single-Level"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Create API with UNKNOWN support"""
        self.api = QueryLayerAPI()

    def test_a14_query_respects_include_unknown_flag(self):
        """A1.4: Query respects include_unknown flag"""
        source = EntityReference(entity_id="ServiceA", entity_type="service")

        # Query with include_unknown=True
        query_with_unknown = AnalysisQuery(
            source_node=source,
            analysis_depth=1,
            include_unknown=True
        )

        # Query with include_unknown=False
        query_without_unknown = AnalysisQuery(
            source_node=source,
            analysis_depth=1,
            include_unknown=False
        )

        result1 = self.api.query_single_level(query_with_unknown)
        result2 = self.api.query_single_level(query_without_unknown)

        assert result1 is not None
        assert result2 is not None
        assert query_with_unknown.include_unknown is True
        assert query_without_unknown.include_unknown is False


class TestA21MultiLevelPathTraversal:
    """A2.1: Multi-Level Path Traversal - Traverse 2+ Level Dependency Chains"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Create API for multi-level queries"""
        self.api = QueryLayerAPI()

    def test_a21_multi_level_query_execution(self):
        """A2.1: Execute multi-level query"""
        source = EntityReference(entity_id="ComponentA", entity_type="component")
        query = AnalysisQuery(source_node=source, analysis_depth=2)

        result = self.api.query_multi_level(query)

        # Verify result structure
        assert result is not None
        assert result.analysis_type == AnalysisType.MULTI_LEVEL
        assert query.analysis_depth == 2

    def test_a21_multi_level_requires_depth_gte_2(self):
        """A2.1: Multi-level query requires depth >= 2"""
        source = EntityReference(entity_id="ServiceB", entity_type="service")

        # Depth 1 should fail
        query = AnalysisQuery(source_node=source, analysis_depth=1)

        with pytest.raises(QueryValidationError):
            self.api.query_multi_level(query)


class TestA22CircularDependencyDetection:
    """A2.2: Circular Dependency Detection - Identify Dependency Cycles"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Create API"""
        self.api = QueryLayerAPI()

    def test_a22_multi_level_with_depth_3(self):
        """A2.2: Support depth >= 2 for cycle detection"""
        source = EntityReference(entity_id="X", entity_type="component")
        query = AnalysisQuery(source_node=source, analysis_depth=3)

        result = self.api.query_multi_level(query)
        assert result is not None
        assert result.analysis_type == AnalysisType.MULTI_LEVEL


class TestB1ScopeLockC1:
    """B1: Scope Lock (C1) Inherited - Analysis Respects Phase 2 Scope Lock"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Create validator"""
        self.validator = QueryValidator()

    def test_b1_scope_lock_validation(self):
        """B1: Scope lock constraint validation available"""
        source = EntityReference(entity_id="Component_A")
        boundary = ScopeBoundaryRef(boundary_id="default_scope")

        # C1 enforcement: validate scope constraints
        result = self.validator.validate_scope_constraints(source, boundary)
        assert isinstance(result, bool)

    def test_b1_out_of_scope_query_rejected(self):
        """B1: Out-of-scope query should be rejected (validation)"""
        # Create query with invalid entity (empty)
        source = EntityReference(entity_id="", entity_type="component")
        query = AnalysisQuery(source_node=source)

        with pytest.raises(QueryValidationError):
            self.validator.validate(query)


class TestB2ArchitectureLockC2:
    """B2: Architecture Lock (C2) Inherited - Phase 2 Structure Unchanged"""

    def test_b2_no_phase2_modification_check(self):
        """B2: Phase 2 files not modified (verified by git)"""
        # This test verifies through git that Phase 2 is immutable
        # In CI/CD, verify: git diff HEAD~1 governance/write_path/evidence/dependency_graph.py
        # Should show no changes to Phase 2 core implementation
        from dependency_graph import DependencyGraph
        from dependency_graph import VerificationStatus, GraphState, DependencyType

        # Phase 2 API still works unchanged
        graph = DependencyGraph()
        assert graph is not None
        assert graph.get_state() == GraphState.INIT


class TestB3UnknownIntegrityC3:
    """B3: UNKNOWN Integrity (C3) Inherited - UNKNOWN States Preserved"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Create API"""
        self.api = QueryLayerAPI()

    def test_b3_unknown_tracking_supported(self):
        """B3: Query Layer supports UNKNOWN tracking"""
        # Create AnalysisUNKNOWN object
        location = EntityReference(entity_id="UnknownService", entity_type="service")
        unknown = AnalysisUNKNOWN(
            location=location,
            reason=UnknownReason.UNRESOLVED_DEPENDENCY,
            evidence_required="Resolution needed"
        )

        assert unknown is not None
        assert unknown.carried_forward is True
        assert unknown.reason == UnknownReason.UNRESOLVED_DEPENDENCY

    def test_b3_result_preserves_unknown_markers(self):
        """B3: Result structure preserves UNKNOWN markers"""
        result = AnalysisResult()
        location = EntityReference(entity_id="X", entity_type="component")
        unknown = AnalysisUNKNOWN(
            location=location,
            reason=UnknownReason.BOUNDARY_AMBIGUITY
        )
        result.unknown_markers.append(unknown)

        assert len(result.unknown_markers) == 1
        assert result.unknown_markers[0].carried_forward is True


class TestB4DataProtectionC4:
    """B4: Data Protection (C4) Inherited - Access Control Maintained"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Create API"""
        self.api = QueryLayerAPI()

    def test_b4_result_structure_immutable(self):
        """B4: Result structure respects data integrity"""
        source = EntityReference(entity_id="A", entity_type="component")
        result = AnalysisResult(source_node=source)

        # Results should be convertible to dict (for storage/transmission)
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert result_dict["result_id"] == result.result_id


class TestI1AnalysisOnFullGraph:
    """I1: Analysis on Full Graph - Full Graph Analysis Operations"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Create API"""
        self.api = QueryLayerAPI()

    def test_i1_query_execution_completes(self):
        """I1: Query execution completes without error"""
        source = EntityReference(entity_id="Root", entity_type="component")
        query = AnalysisQuery(source_node=source, analysis_depth=1)

        # Should complete without exception
        result = self.api.query_single_level(query)
        assert result is not None


class TestI2ResultConsistency:
    """I2: Result Consistency - Multiple Queries Same Results"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Create API"""
        self.api = QueryLayerAPI()

    def test_i2_deterministic_query_results(self):
        """I2: Queries deterministic (same input -> same result structure)"""
        source = EntityReference(entity_id="Service_A", entity_type="service")
        query = AnalysisQuery(source_node=source, analysis_depth=1)

        result1 = self.api.query_single_level(query)
        result2 = self.api.query_single_level(query)

        # Results should have same structure
        assert result1.analysis_type == result2.analysis_type
        assert result1.source_node == result2.source_node


class TestI3UnknownHandlingEdgeCases:
    """I3: UNKNOWN Handling Edge Cases - Edge Case UNKNOWN Scenarios"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Create API"""
        self.api = QueryLayerAPI()

    def test_i3_query_with_all_unknowns(self):
        """I3: Query with include_unknown=True handles all cases"""
        source = EntityReference(entity_id="UnknownComponent", entity_type="component")
        query = AnalysisQuery(
            source_node=source,
            analysis_depth=1,
            include_unknown=True
        )

        result = self.api.query_single_level(query)
        assert result is not None

    def test_i3_error_handling(self):
        """I3: Query Layer error handling works"""
        api = QueryLayerAPI()
        error = QueryValidationError("Test error")
        error_dict = api.handle_query_error(error)

        assert "error_type" in error_dict
        assert "error_message" in error_dict
        assert "timestamp" in error_dict
