"""Run every trial case and emit audit records.

Usage:
    python -m experiments.constitutional_runtime_trial.run_trial [--json PATH]

Isolation: this runner touches nothing outside its own results directory. It
does not write to events.db, the Decision Ledger, or any production store.
"""

import argparse
import os
import sys

from .audit import AuditRecord, to_json, to_markdown_table
from .runtime_basic import ConstitutionalRuntimeBasic
from .runtime_extended import ConstitutionalRuntimeExtended
from .suites import ALL_CASES, NOW

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
DEFAULT_JSON = os.path.join(RESULTS_DIR, "trial_results.json")


def evaluate_case(case):
    """Run one case on a fresh runtime and return its Evaluation."""
    if case.tier == "basic":
        runtime = ConstitutionalRuntimeBasic()
        for primer in case.prime:
            runtime.evaluate(primer, now=NOW)
        return runtime.evaluate(case.raw, now=NOW)

    runtime = ConstitutionalRuntimeExtended()
    for primer in case.prime:
        runtime.evaluate(primer, now=NOW)
    return runtime.evaluate(case.raw, context=case.context, now=NOW)


def _structured_summary(evaluation):
    intake = evaluation.intake
    if intake is None or intake.contract is None:
        return "none (no inspectable contract)"
    typed = len([k for k, v in intake.contract.typed.items() if v is not None])
    prose = len(intake.contract.prose_keys())
    return "%d typed field(s), %d prose field(s) quarantined" % (typed, prose)


def build_records():
    records = []
    for case in ALL_CASES:
        evaluation = evaluate_case(case)
        records.append(
            AuditRecord(
                test_id=case.test_id,
                title=case.title,
                runtime=evaluation.runtime,
                input_summary=case.input_summary,
                structured_contract=_structured_summary(evaluation),
                primitives=evaluation.primitives,
                expected_decision=case.expected,
                actual_decision=evaluation.decision.value,
                actual_execution=evaluation.execution.value,
                evidence_status=case.evidence_status,
                reason=evaluation.reason,
            )
        )
    return records


def main(argv=None):
    parser = argparse.ArgumentParser(description="MoCKA CR Trial runner")
    parser.add_argument("--json", default=DEFAULT_JSON, help="path for the audit JSON output")
    parser.add_argument("--markdown", action="store_true", help="print the markdown table")
    args = parser.parse_args(argv)

    records = build_records()

    if not os.path.isdir(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
    with open(args.json, "w", encoding="utf-8") as handle:
        handle.write(to_json(records))
        handle.write("\n")

    if args.markdown:
        print(to_markdown_table(records))
    else:
        for record in records:
            print(
                "%-16s %-9s expected=%-16s actual=%-8s exec=%-8s %s"
                % (
                    record.test_id,
                    record.verdict,
                    "|".join(record.expected_decision),
                    record.actual_decision,
                    record.actual_execution,
                    ",".join(record.primitives) if record.primitives else "-",
                )
            )

    failed = [r for r in records if r.verdict == "FAIL"]
    allowed = [r for r in records if r.actual_execution == "EXECUTE"]
    print(
        "\n%d case(s), %d pass, %d fail, %d reached EXECUTE (%s)"
        % (
            len(records),
            len(records) - len(failed),
            len(failed),
            len(allowed),
            ", ".join(r.test_id for r in allowed) if allowed else "none",
        )
    )
    print("audit json: %s" % args.json)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
