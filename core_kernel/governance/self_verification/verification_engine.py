"""Self Verification Engine.

Checks that, for every Requirement in requirement_map.REQUIREMENTS,
the chain

    Design -> Contract -> Implementation -> Unit Test
           -> Integration Test -> Evidence

is present and consistent. Self Verification does not grade test
quality or re-derive Governance decisions; it confirms:

  1. each layer's file exists ("the link is not missing")
  2. the test suite passes ("the link is not broken")
  3. Evidence collected from a real run matches the shape the design
     promises (PASS -> committed, FAIL -> blocked, etc.)
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from ..engines.decision_engine import DecisionResult
from .evidence import EvidenceBundle, collect_evidence
from .requirement_map import REQUIREMENTS, Requirement
from .traceability import (
    ClosureReport,
    CoverageMatrix,
    DriftFinding,
    TraceGraph,
    build_coverage_matrix,
    build_trace_graph,
    check_closure,
    detect_drift,
)

MOCKA_ROOT = Path(__file__).resolve().parents[3]


class VerificationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


@dataclass(frozen=True)
class RequirementResult:
    requirement: Requirement
    status: VerificationStatus
    missing_links: tuple[str, ...]


@dataclass(frozen=True)
class VerificationReport:
    status: VerificationStatus
    requirement_results: tuple[RequirementResult, ...]
    test_exit_code: int
    test_output_tail: str
    evidence: EvidenceBundle
    evidence_findings: tuple[str, ...]
    trace_graph: TraceGraph
    coverage_matrix: CoverageMatrix
    closure: ClosureReport
    drift_findings: tuple[DriftFinding, ...]


_LAYER_FIELDS = ("design", "contract", "unit_test", "integration_test")


def _check_requirement_files(req: Requirement, root: Path) -> tuple[str, ...]:
    missing: list[str] = []
    for field_name in _LAYER_FIELDS:
        path = getattr(req, field_name)
        if path is None:
            continue
        if not (root / path).exists():
            missing.append(f"{field_name}:{path}")
    for impl in req.implementation:
        if not (root / impl).exists():
            missing.append(f"implementation:{impl}")
    return tuple(missing)


# Tests that themselves call SelfVerificationEngine.run() must be
# excluded from the subprocess scan below, or they would re-spawn this
# subprocess recursively.
_RECURSIVE_TESTS = (
    "core_kernel/governance/tests/unit/test_self_verification.py",
    "core_kernel/governance/tests/unit/test_intelligence.py",
)


def _run_tests(root: Path) -> tuple[int, str]:
    ignore_args: list[str] = []
    for rel in _RECURSIVE_TESTS:
        ignore_args += ["--ignore", str(root / rel)]
    proc = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            str(root / "core_kernel/governance/tests"), "-q",
            *ignore_args,
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )
    output = proc.stdout + proc.stderr
    return proc.returncode, output[-2000:]


def _check_evidence(evidence: EvidenceBundle) -> tuple[str, ...]:
    """Verify Evidence matches what each scenario's design contract
    promises. Returns a tuple of finding strings; empty == all good."""

    findings: list[str] = []

    expectations = {
        "pass": (DecisionResult.PASS, True, "COMMITTED"),
        "warning": (DecisionResult.WARNING, True, "COMMITTED"),
        "fail": (DecisionResult.FAIL, False, "BLOCKED"),
    }

    for name, (expected_decision, expected_committed, expected_audit_decision) in expectations.items():
        result = evidence.results[name]
        if result.commit.decision is not expected_decision:
            findings.append(
                f"{name}: decision={result.commit.decision} expected={expected_decision}"
            )
        if result.commit.committed is not expected_committed:
            findings.append(
                f"{name}: committed={result.commit.committed} expected={expected_committed}"
            )

        event_id = result.pipeline.event.event_id
        commit_audit = [
            r for r in evidence.audit_records if r.event_id == event_id and r.engine == "GovernanceRuntime"
        ]
        if len(commit_audit) != 1:
            findings.append(f"{name}: expected exactly 1 GovernanceRuntime audit record, got {len(commit_audit)}")
        elif commit_audit[0].decision != expected_audit_decision:
            findings.append(
                f"{name}: audit decision={commit_audit[0].decision} expected={expected_audit_decision}"
            )

    return tuple(findings)


class SelfVerificationEngine:
    """Runs the Design -> ... -> Evidence consistency check."""

    def __init__(self, root: Path | None = None) -> None:
        self._root = root or MOCKA_ROOT

    def run(self) -> VerificationReport:
        requirement_results = []
        for req in REQUIREMENTS:
            missing = _check_requirement_files(req, self._root)
            status = VerificationStatus.FAIL if missing else VerificationStatus.PASS
            requirement_results.append(RequirementResult(req, status, missing))

        exit_code, output_tail = _run_tests(self._root)
        evidence = collect_evidence()
        evidence_findings = _check_evidence(evidence)

        graph = build_trace_graph(evidence, self._root)
        coverage = build_coverage_matrix(graph)
        closure = check_closure(graph)
        drift_findings = detect_drift(evidence, self._root)

        overall = VerificationStatus.PASS
        if any(r.status is VerificationStatus.FAIL for r in requirement_results):
            overall = VerificationStatus.FAIL
        if exit_code != 0:
            overall = VerificationStatus.FAIL
        if evidence_findings:
            overall = VerificationStatus.FAIL
        if not closure.is_closed:
            overall = VerificationStatus.FAIL
        if drift_findings:
            overall = VerificationStatus.FAIL

        return VerificationReport(
            status=overall,
            requirement_results=tuple(requirement_results),
            test_exit_code=exit_code,
            test_output_tail=output_tail,
            evidence=evidence,
            evidence_findings=evidence_findings,
            trace_graph=graph,
            coverage_matrix=coverage,
            closure=closure,
            drift_findings=drift_findings,
        )
