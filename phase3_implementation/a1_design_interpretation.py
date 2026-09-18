"""
HG-M3 Phase 3: Component A1 - Design Interpretation

Translate Human Gate Q1-Q6 decisions into code specifications.
Map decision options (A/B/C) to implementation logic.
Define configuration structures for policy storage.

Status: DESIGN LAYER ONLY (no runtime activation)
Environment: SANDBOX ONLY
"""

import json
from typing import Dict, List, Any


class Q1Q6Configuration:
    """Q1-Q6 Decision to Code Specification Mapping"""

    # Q1: Evidence Binding Model
    Q1_OPTIONS = {
        "A": {
            "name": "Explicit Binding",
            "description": "Evidence must be explicitly bound to decision",
            "requirement": "All evidence sources must be declared upfront",
            "check_type": "pre_binding"
        },
        "B": {
            "name": "Dynamic Binding",
            "description": "Evidence can be added/modified during validation",
            "requirement": "Evidence binding can evolve with decision lifecycle",
            "check_type": "continuous_binding"
        },
        "C": {
            "name": "Retroactive Binding",
            "description": "Evidence can be added after decision is made",
            "requirement": "Must track evidence temporal ordering",
            "check_type": "retroactive_binding"
        }
    }

    # Q2: Authority Retroactive Registration
    Q2_OPTIONS = {
        "A": {
            "name": "Prospective Only",
            "description": "Authority must be registered before use",
            "requirement": "No retroactive authority registration allowed",
            "enforcement": "pre_check_only"
        },
        "B": {
            "name": "Limited Retroactive",
            "description": "Authority can be registered within time window",
            "requirement": "Retroactive registration allowed up to N days",
            "enforcement": "time_windowed_check"
        },
        "C": {
            "name": "Unrestricted Retroactive",
            "description": "Authority can be registered anytime",
            "requirement": "Retroactive registration always allowed",
            "enforcement": "post_check_ok"
        }
    }

    # Q3: Validation Failure Escalation
    Q3_OPTIONS = {
        "A": {
            "name": "Human Gate Always",
            "description": "All failures escalate to Human Gate",
            "requirement": "No automatic resolution of failures",
            "escalation_rule": "all_failures_to_hg"
        },
        "B": {
            "name": "Conditional Escalation",
            "description": "Minor failures auto-resolved, major ones to HG",
            "requirement": "Categorize failures by severity",
            "escalation_rule": "severity_based"
        },
        "C": {
            "name": "Auto-Resolution with Log",
            "description": "Failures auto-resolved with logging only",
            "requirement": "Must maintain full audit trail",
            "escalation_rule": "auto_with_audit"
        }
    }

    # Q4: Evidence Integrity Verification
    Q4_OPTIONS = {
        "A": {
            "name": "Hash-Chain Verification",
            "description": "Use cryptographic hash chains",
            "requirement": "Detect retroactive insertion via hash breaks",
            "verification_method": "hash_chain"
        },
        "B": {
            "name": "Timestamp Ordering",
            "description": "Verify evidence temporal ordering",
            "requirement": "Evidence timestamps must be monotonically increasing",
            "verification_method": "timestamp_ordering"
        },
        "C": {
            "name": "Dual Verification",
            "description": "Hash-chain AND timestamp ordering",
            "requirement": "Both hash integrity and temporal correctness",
            "verification_method": "hash_and_timestamp"
        }
    }

    # Q5: Continuous Monitoring
    Q5_OPTIONS = {
        "A": {
            "name": "Spot Checks",
            "description": "Random periodic verification",
            "requirement": "Check integrity at random intervals",
            "monitoring_frequency": "random"
        },
        "B": {
            "name": "Scheduled Monitoring",
            "description": "Regular scheduled verification",
            "requirement": "Check integrity on fixed schedule (hourly/daily)",
            "monitoring_frequency": "scheduled"
        },
        "C": {
            "name": "Continuous Monitoring",
            "description": "Real-time verification of all state changes",
            "requirement": "24/7 monitoring of evidence/authority/config",
            "monitoring_frequency": "continuous"
        }
    }

    # Q6: Failure Recovery Strategy
    Q6_OPTIONS = {
        "A": {
            "name": "Manual Recovery",
            "description": "Human Gate approves all recovery actions",
            "requirement": "No automatic rollback; HG approval required",
            "recovery_type": "manual_approval"
        },
        "B": {
            "name": "Automatic Recovery with Notification",
            "description": "Auto-rollback then notify HG",
            "requirement": "Rollback happens automatically, HG notified post-action",
            "recovery_type": "auto_then_notify"
        },
        "C": {
            "name": "Automatic Recovery with Audit",
            "description": "Auto-rollback with full audit trail",
            "requirement": "Rollback + comprehensive logging + HG review",
            "recovery_type": "auto_with_audit"
        }
    }

    def __init__(self, decisions: Dict[str, str]):
        """
        Initialize with Q1-Q6 decisions

        Args:
            decisions: Dict with keys Q1-Q6, values A/B/C
        """
        self.decisions = decisions
        self.config = self._build_configuration()

    def _build_configuration(self) -> Dict[str, Any]:
        """Build configuration from Q1-Q6 decisions"""
        config = {
            "metadata": {
                "phase": "PHASE3",
                "environment": "sandbox",
                "version": "1.0",
                "decisions": self.decisions
            },
            "q1_evidence_binding": self.Q1_OPTIONS.get(self.decisions.get("Q1")),
            "q2_authority_registration": self.Q2_OPTIONS.get(self.decisions.get("Q2")),
            "q3_failure_escalation": self.Q3_OPTIONS.get(self.decisions.get("Q3")),
            "q4_evidence_verification": self.Q4_OPTIONS.get(self.decisions.get("Q4")),
            "q5_monitoring": self.Q5_OPTIONS.get(self.decisions.get("Q5")),
            "q6_recovery": self.Q6_OPTIONS.get(self.decisions.get("Q6"))
        }
        return config

    def get_evidence_binding_check_type(self) -> str:
        """Q1: Which type of evidence binding check?"""
        return self.config["q1_evidence_binding"]["check_type"]

    def get_authority_enforcement_rule(self) -> str:
        """Q2: Which authority registration enforcement rule?"""
        return self.config["q2_authority_registration"]["enforcement"]

    def get_escalation_rule(self) -> str:
        """Q3: Which escalation rule for failures?"""
        return self.config["q3_failure_escalation"]["escalation_rule"]

    def get_verification_method(self) -> str:
        """Q4: Which evidence verification method?"""
        return self.config["q4_evidence_verification"]["verification_method"]

    def get_monitoring_frequency(self) -> str:
        """Q5: Which monitoring frequency?"""
        return self.config["q5_monitoring"]["monitoring_frequency"]

    def get_recovery_type(self) -> str:
        """Q6: Which recovery strategy?"""
        return self.config["q6_recovery"]["recovery_type"]

    def export_policy(self) -> Dict[str, Any]:
        """Export full policy configuration"""
        return self.config

    def export_json(self) -> str:
        """Export configuration as JSON"""
        return json.dumps(self.config, indent=2, ensure_ascii=True)


class PolicyValidator:
    """Validate that policy configuration is consistent"""

    @staticmethod
    def validate_consistency(config: Dict[str, Any]) -> List[str]:
        """
        Validate policy consistency across Q1-Q6

        Returns:
            List of validation issues (empty if valid)
        """
        issues = []

        # Check Q4-Q5 consistency: continuous monitoring requires hash-chain or dual
        q5_freq = config.get("q5_monitoring", {}).get("monitoring_frequency")
        q4_method = config.get("q4_evidence_verification", {}).get("verification_method")

        if q5_freq == "continuous" and q4_method not in ["hash_chain", "hash_and_timestamp"]:
            issues.append(
                "Q5=Continuous monitoring requires Q4=Hash-Chain or Dual verification"
            )

        # Check Q3-Q6 consistency: auto-resolution requires auto-recovery
        q3_rule = config.get("q3_failure_escalation", {}).get("escalation_rule")
        q6_type = config.get("q6_recovery", {}).get("recovery_type")

        if q3_rule == "auto_with_audit" and q6_type == "manual_approval":
            issues.append(
                "Q3=Auto-Resolution requires Q6=Automatic recovery, not manual"
            )

        return issues


# Example usage and testing
if __name__ == "__main__":
    # Example: Q1-Q6 decisions from Human Gate
    example_decisions = {
        "Q1": "B",  # Dynamic Binding
        "Q2": "A",  # Prospective Only
        "Q3": "A",  # Human Gate Always
        "Q4": "C",  # Dual Verification
        "Q5": "C",  # Continuous Monitoring
        "Q6": "C"   # Auto with Audit
    }

    config = Q1Q6Configuration(example_decisions)
    policy = config.export_policy()

    print("Design Interpretation - Q1-Q6 Policy Configuration")
    print("=" * 60)
    print(config.export_json())

    print("\nPolicy Consistency Check")
    print("=" * 60)
    issues = PolicyValidator.validate_consistency(policy)
    if issues:
        print(f"Issues found: {len(issues)}")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ Policy is consistent")
