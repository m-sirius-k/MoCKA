"""Audit record for the MoCKA CR Trial.

Every executed case produces one record with the fields required by the trial
specification, section 18:

    Test ID / Input / Structured Contract / Primitive / Expected Decision /
    Actual Decision / Evidence Status / Reason

Evidence Status is about the PROVENANCE OF THE EXPECTATION, not about whether
the test passed. It answers "where does the expected value come from".

    OBSERVED  - reported from the 50-test boundary experiment
    DERIVED   - follows from an OBSERVED item plus stated reasoning
    DESIGNED  - fixed by this trial's own specification
    PROPOSED  - offered for review, not yet fixed
    UNKNOWN   - cannot be established from available evidence
"""

import json

EVIDENCE_STATUSES = ("OBSERVED", "DERIVED", "DESIGNED", "PROPOSED", "UNKNOWN")


class AuditRecord(object):
    __slots__ = (
        "test_id",
        "title",
        "runtime",
        "input_summary",
        "structured_contract",
        "primitives",
        "expected_decision",
        "actual_decision",
        "actual_execution",
        "evidence_status",
        "reason",
        "verdict",
    )

    def __init__(
        self,
        test_id,
        title,
        runtime,
        input_summary,
        structured_contract,
        primitives,
        expected_decision,
        actual_decision,
        actual_execution,
        evidence_status,
        reason,
    ):
        if evidence_status not in EVIDENCE_STATUSES:
            raise ValueError("unknown evidence status %r" % (evidence_status,))
        self.test_id = test_id
        self.title = title
        self.runtime = runtime
        self.input_summary = input_summary
        self.structured_contract = structured_contract
        self.primitives = primitives
        self.expected_decision = expected_decision
        self.actual_decision = actual_decision
        self.actual_execution = actual_execution
        self.evidence_status = evidence_status
        self.reason = reason
        self.verdict = "PASS" if actual_decision in expected_decision else "FAIL"

    def as_dict(self):
        return {
            "test_id": self.test_id,
            "title": self.title,
            "runtime": self.runtime,
            "input": self.input_summary,
            "structured_contract": self.structured_contract,
            "primitive": self.primitives,
            "expected_decision": list(self.expected_decision),
            "actual_decision": self.actual_decision,
            "actual_execution": self.actual_execution,
            "evidence_status": self.evidence_status,
            "reason": self.reason,
            "result": self.verdict,
        }


def to_json(records, indent=2):
    return json.dumps([r.as_dict() for r in records], ensure_ascii=False, indent=indent)


def to_markdown_table(records):
    header = (
        "| Test ID | Runtime | Structured Contract | Primitive | Expected | Actual | Execution | Evidence | Result |\n"
        "| ------- | ------- | ------------------- | --------- | -------- | ------ | --------- | -------- | ------ |\n"
    )
    rows = []
    for r in records:
        rows.append(
            "| %s | %s | %s | %s | %s | %s | %s | %s | %s |"
            % (
                r.test_id,
                "Basic" if "Basic" in r.runtime else "Extended",
                r.structured_contract,
                ", ".join(r.primitives) if r.primitives else "-",
                " or ".join(r.expected_decision),
                r.actual_decision,
                r.actual_execution,
                r.evidence_status,
                r.verdict,
            )
        )
    return header + "\n".join(rows)
