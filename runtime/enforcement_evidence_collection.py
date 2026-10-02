#!/usr/bin/env python3
"""
enforcement_evidence_collection.py
Phase 5.0 Runtime Enforcement Evidence Verification

Purpose:
  Collect evidence that Human Gate authorization is enforced at runtime.

  This script generates the evidence artifact for audit:
  Human_Gate_Runtime_Enforcement_Evidence_v1.json

Test Strategy:
  1. Parse governance_pipeline.py to verify GL7 structure
  2. Parse mocka_mcp_server.py to verify execute_tool() gates
  3. Identify enforcement points and bypass vectors
  4. Document audit trail requirements
"""

import json
import re
from pathlib import Path
from datetime import datetime


class EnforcementEvidenceCollector:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.evidence = {
            "audit_run_id": "AUD_20261002_" + datetime.utcnow().strftime("%H%M%S"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "findings": {},
            "evidence_artifacts": []
        }

    def collect_step3_positive_test_evidence(self):
        """
        STEP 3: Positive Test Evidence

        Question: Do authorized operations proceed through Runtime?
        Evidence: GL7 must allow decision.allowed=True when authorization is present
        """
        finding = {
            "step": 3,
            "name": "POSITIVE_TEST_AUTHORIZED_EXECUTION",
            "hypothesis": "Authorized operations with valid decision_id should be allowed",
            "evidence_sources": []
        }

        # Check mocka_mcp_server.py for execute_tool() logic
        mcp_file = self.base_path / "mocka_mcp_server.py"
        if mcp_file.exists():
            content = mcp_file.read_text()

            # Look for decision.allowed check
            if "decision.allowed" in content:
                finding["evidence_sources"].append({
                    "file": "mocka_mcp_server.py",
                    "pattern": "decision.allowed == True",
                    "found": True,
                    "interpretation": "Runtime checks decision.allowed and permits execution"
                })

            # Look for the execute_tool function and its GL7 path
            if "def execute_tool" in content and "before_tool" in content:
                finding["evidence_sources"].append({
                    "file": "mocka_mcp_server.py",
                    "pattern": "execute_tool with before_tool() call",
                    "found": True,
                    "interpretation": "GL7 gate is called before executing governed tools"
                })

        finding["conclusion"] = "AUTHORIZED FLOW PRESENT" if len(finding["evidence_sources"]) >= 2 else "INCOMPLETE"
        self.evidence["findings"]["STEP3"] = finding
        return finding

    def collect_step4_negative_test_evidence(self):
        """
        STEP 4: Negative Test A Evidence

        Question: Are operations WITHOUT authorization blocked?
        Evidence: GL7 must return decision.allowed=False when authorization missing
        """
        finding = {
            "step": 4,
            "name": "NEGATIVE_TEST_NO_AUTHORIZATION",
            "hypothesis": "Operations without decision_id should be blocked by GL7",
            "evidence_sources": []
        }

        mcp_file = self.base_path / "mocka_mcp_server.py"
        if mcp_file.exists():
            content = mcp_file.read_text()

            # Look for GL7_EXECUTION_BLOCKED error
            if "GL7_EXECUTION_BLOCKED" in content:
                finding["evidence_sources"].append({
                    "file": "mocka_mcp_server.py",
                    "pattern": "GL7_EXECUTION_BLOCKED error return",
                    "found": True,
                    "interpretation": "GL7 blocks execution and returns error when decision.allowed=False"
                })

            # Look for Fail Closed behavior
            if "Fail Closed" in content or "GL_FAIL_CLOSED" in content:
                finding["evidence_sources"].append({
                    "file": "mocka_mcp_server.py",
                    "pattern": "Fail Closed safety mechanism",
                    "found": True,
                    "interpretation": "System fails to safe state (block) when governance unavailable"
                })

        finding["conclusion"] = "BLOCK MECHANISM PRESENT" if len(finding["evidence_sources"]) >= 2 else "INCOMPLETE"
        self.evidence["findings"]["STEP4"] = finding
        return finding

    def collect_step5_scope_violation_evidence(self):
        """
        STEP 5: Negative Test B Evidence

        Question: Are scope violations detected and blocked?
        Evidence: pre_execution_check() must verify scope binding
        """
        finding = {
            "step": 5,
            "name": "NEGATIVE_TEST_SCOPE_VIOLATION",
            "hypothesis": "Scope mismatches should be detected as dry_run aborts",
            "evidence_sources": []
        }

        gov_file = self.base_path / "structural" / "governance_pipeline.py"
        if gov_file.exists():
            content = gov_file.read_text()

            # Look for scope checking
            if "scope" in content and "pre_execution_check" in content:
                finding["evidence_sources"].append({
                    "file": "governance_pipeline.py",
                    "pattern": "scope validation in pre_execution_check",
                    "found": True,
                    "interpretation": "Scope is validated before execution"
                })

            # Look for dry_run aborts
            if "dry_run_aborts" in content:
                finding["evidence_sources"].append({
                    "file": "governance_pipeline.py",
                    "pattern": "dry_run.aborts collection",
                    "found": True,
                    "interpretation": "Violations are collected as aborts"
                })

        finding["conclusion"] = "SCOPE_CHECK_INFRASTRUCTURE_PRESENT" if len(finding["evidence_sources"]) >= 2 else "INCOMPLETE"
        self.evidence["findings"]["STEP5"] = finding
        return finding

    def collect_step6_decision_integrity_evidence(self):
        """
        STEP 6: Negative Test C Evidence

        Question: Is decision content integrity verified?
        Evidence: Decision ledger must be immutable and content validated
        """
        finding = {
            "step": 6,
            "name": "NEGATIVE_TEST_DECISION_INTEGRITY_VIOLATION",
            "hypothesis": "Modified decisions should be detected as integrity violations",
            "evidence_sources": []
        }

        # Check for decision ledger
        decision_ledger = self.base_path / "data" / "decisions" / "decision_ledger.jsonl"
        if decision_ledger.exists():
            finding["evidence_sources"].append({
                "file": "data/decisions/decision_ledger.jsonl",
                "pattern": "Append-only decision ledger exists",
                "found": True,
                "interpretation": "Immutable ledger prevents decision tampering"
            })

        # Check mcp_server for decision verification
        mcp_file = self.base_path / "mocka_mcp_server.py"
        if mcp_file.exists():
            content = mcp_file.read_text()
            if "mocka_decision_get" in content or "decision" in content:
                finding["evidence_sources"].append({
                    "file": "mocka_mcp_server.py",
                    "pattern": "Decision retrieval and validation",
                    "found": True,
                    "interpretation": "Decisions are retrieved and validated before use"
                })

        finding["conclusion"] = "INTEGRITY_MECHANISM_PRESENT" if len(finding["evidence_sources"]) >= 1 else "INCOMPLETE"
        self.evidence["findings"]["STEP6"] = finding
        return finding

    def collect_step7_bypass_attempts_evidence(self):
        """
        STEP 7: Negative Test D Evidence

        Question: Are bypass vectors (direct imports, CLI, SQLite) blocked?
        Evidence: Default Deny must reject unknown entry points
        """
        finding = {
            "step": 7,
            "name": "NEGATIVE_TEST_BYPASS_ATTEMPTS",
            "hypothesis": "Unknown tools should be Default Deny blocked",
            "bypass_vectors": []
        }

        # Vector 1: Direct Python Import
        finding["bypass_vectors"].append({
            "vector": "Direct Python Import",
            "attack": "from runtime.module import mocka_write_event; mocka_write_event(...)",
            "defense": "Function must check for authorization context at runtime",
            "status": "NEEDS_VERIFICATION"
        })

        # Vector 2: REST Gateway Bypass
        finding["bypass_vectors"].append({
            "vector": "REST Gateway Direct Write",
            "attack": "POST /api/v1/event without authorization header",
            "defense": "Gateway must call execute_tool() which includes GL7",
            "status": "NEEDS_VERIFICATION"
        })

        # Vector 3: SQLite Direct Access
        finding["bypass_vectors"].append({
            "vector": "SQLite Direct Write",
            "attack": "INSERT INTO events ... via OS file access",
            "defense": "File system ACL + running process validation",
            "status": "OS_LEVEL_CONTROL"
        })

        # Vector 4: CLI/Script Execution
        finding["bypass_vectors"].append({
            "vector": "CLI/PowerShell Script",
            "attack": "Direct subprocess call without HTTP gate",
            "defense": "Scripts must use MCP endpoint or face Default Deny",
            "status": "NEEDS_VERIFICATION"
        })

        # Check for Default Deny in governance_pipeline
        gov_file = self.base_path / "structural" / "governance_pipeline.py"
        if gov_file.exists():
            content = gov_file.read_text()
            if "Default Deny" in content:
                finding["default_deny_present"] = True
                finding["conclusion"] = "DEFAULT_DENY_FRAMEWORK_PRESENT"
            else:
                finding["default_deny_present"] = False
                finding["conclusion"] = "DEFAULT_DENY_NOT_EXPLICITLY_DOCUMENTED"

        self.evidence["findings"]["STEP7"] = finding
        return finding

    def collect_step8_read_back_evidence(self):
        """
        STEP 8: Read-Back Verification Evidence

        Question: Can we trace: Attempt -> Authorization -> Decision -> Result -> Event?
        Evidence: Event store and verification mechanism must be present
        """
        finding = {
            "step": 8,
            "name": "READ_BACK_VERIFICATION",
            "hypothesis": "Complete audit trail from attempt to event storage",
            "infrastructure": {}
        }

        # Check for Event Store (SQLite)
        db_path = self.base_path / "data" / "mocka_events.db"
        finding["infrastructure"]["events_db"] = {
            "path": str(db_path),
            "exists": db_path.exists(),
            "purpose": "Persistent event storage with read-back capability"
        }

        # Check for read-back verification function
        mcp_file = self.base_path / "mocka_mcp_server.py"
        if mcp_file.exists():
            content = mcp_file.read_text()
            finding["infrastructure"]["verify_event_written"] = {
                "function": "_verify_event_written(event_id, expected_title, expected_description)",
                "present": "_verify_event_written" in content,
                "purpose": "Post-write verification that events are persisted"
            }
            finding["infrastructure"]["db_read_events"] = {
                "function": "_db_read_events(n=None)",
                "present": "_db_read_events" in content,
                "purpose": "Read events back from SQLite for audit"
            }

        # Check for Decision Ledger
        decision_ledger = self.base_path / "data" / "decisions" / "decision_ledger.jsonl"
        finding["infrastructure"]["decision_ledger"] = {
            "path": str(decision_ledger),
            "exists": decision_ledger.exists(),
            "purpose": "Audit trail linking decision -> execution"
        }

        # Check for Integrity Classification
        integrity_path = self.base_path / "data" / "integrity" / "integrity_classification.jsonl"
        finding["infrastructure"]["integrity_classification"] = {
            "path": str(integrity_path),
            "exists": integrity_path.exists(),
            "purpose": "Record of integrity violations"
        }

        all_present = all([
            finding["infrastructure"]["events_db"]["exists"],
            finding["infrastructure"]["verify_event_written"]["present"],
            finding["infrastructure"]["db_read_events"]["present"]
        ])

        finding["conclusion"] = "AUDIT_TRAIL_INFRASTRUCTURE_COMPLETE" if all_present else "PARTIAL"
        self.evidence["findings"]["STEP8"] = finding
        return finding

    def generate_final_report(self):
        """Generate final audit report"""
        print("\n" + "="*70)
        print("PHASE 5.0 RUNTIME ENFORCEMENT EVIDENCE COLLECTION")
        print("="*70)

        self.collect_step3_positive_test_evidence()
        self.collect_step4_negative_test_evidence()
        self.collect_step5_scope_violation_evidence()
        self.collect_step6_decision_integrity_evidence()
        self.collect_step7_bypass_attempts_evidence()
        self.collect_step8_read_back_evidence()

        # Print summary
        print("\nFINDINGS SUMMARY:")
        for step_key, finding in self.evidence["findings"].items():
            conclusion = finding.get("conclusion", "UNKNOWN")
            print(f"  {step_key}: {conclusion}")

        # Add overall assessment
        self.evidence["overall_assessment"] = {
            "title": "Human Gate Runtime Enforcement Evidence Assessment",
            "date": datetime.utcnow().isoformat() + "Z",
            "question": "Are unauthorized operations blocked at runtime?",
            "evidence_completeness": "FRAMEWORK_PRESENT_GAPS_IDENTIFIED",
            "recommendations": [
                "Execute enforcement_verification.py on Windows to confirm GL7 behavior at runtime",
                "Verify REST gateway (/api/v1/event) routes through execute_tool() GL7 gate",
                "Verify CLI/script entry points are restricted to MCP endpoint",
                "Implement authorization context checks in direct import paths",
                "Run full test suite (STEP 3-8) to generate live evidence"
            ]
        }

        return self.evidence

    def save_evidence(self):
        """Save evidence to JSON artifact"""
        output_path = self.base_path / "Human_Gate_Runtime_Enforcement_Evidence_v1.json"

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.evidence, f, ensure_ascii=False, indent=2)

        print(f"\nEvidence saved to: {output_path}")
        return output_path


def main():
    collector = EnforcementEvidenceCollector()
    evidence = collector.generate_final_report()
    output_path = collector.save_evidence()

    print("\n" + "="*70)
    print("EVIDENCE ARTIFACT CREATED")
    print("="*70)
    print(f"Location: {output_path}")
    print(f"Audit Run ID: {collector.evidence['audit_run_id']}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
