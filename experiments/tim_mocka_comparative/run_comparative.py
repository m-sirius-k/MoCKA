"""Run the comparative matrix and emit an audit record.

Usage:
    python -m experiments.tim_mocka_comparative.run_comparative [--json PATH]

Writes nothing outside this package's results directory.
"""

import argparse
import json
import os
import sys

from .cases import (
    AXES,
    AXIS_VOCAB,
    CASES,
    NOT_TESTED,
    T50_EXPECTED,
    T50_PRESENT,
    T50_RECORD,
    UNKNOWN_AXIS,
    findings_match,
)
from .temporal import ReEvaluationGate, reuse_directly

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
DEFAULT_JSON = os.path.join(RESULTS_DIR, "comparative_results.json")


def score_axes(case, assessment):
    """Score the five axes for one case.

    An axis declared NOT_TESTED stays NOT_TESTED. An axis declared UNKNOWN stays
    UNKNOWN and is never converted to FAIL. Otherwise the axis passes when the
    findings it owns are exactly those the case expects.
    """
    actual = set(assessment.finding_names)
    scores = {}
    for axis in AXES:
        if axis == "re_evaluation_correctness":
            ok = (
                assessment.eligibility.value in case.expected_eligibility
                and assessment.execution.value == case.expected_execution
            )
            scores[axis] = "PASS" if ok else "FAIL"
            continue
        declared = case.axes.get(axis, NOT_TESTED)
        if declared == NOT_TESTED:
            scores[axis] = "NOT_TESTED"
        elif declared == UNKNOWN_AXIS:
            scores[axis] = "UNKNOWN"
        else:
            observed = actual & AXIS_VOCAB[axis]
            scores[axis] = "PASS" if observed == set(declared) else "FAIL"
    return scores


def run_matrix():
    gate = ReEvaluationGate()
    rows = []
    for case in CASES:
        assessment = gate.assess(case.record, case.present)
        scores = score_axes(case, assessment)
        rows.append(
            {
                "case_id": case.case_id,
                "past_decision": case.past,
                "present_state": case.now_state,
                "evidence": {
                    "recorded": case.record.evidence_digest,
                    "present": case.present.evidence_digest,
                },
                "timestamp": {
                    "decided_at": case.record.decided_at,
                    "validity_until": case.record.validity_until,
                    "now": case.present.now,
                },
                "decision": case.record.decision.value,
                "authority": {
                    "recorded": case.record.authority_id,
                    "present": case.present.authority_id,
                    "present_state": case.present.authority_state,
                },
                "validity": case.record.validity_until,
                "current_context": {
                    "recorded_id": case.record.context_id,
                    "present_id": case.present.context_id,
                    "recorded_digest": case.record.context_digest,
                    "present_digest": case.present.context_digest,
                },
                "findings": assessment.finding_names,
                "expected_eligibility": list(case.expected_eligibility),
                "actual_eligibility": assessment.eligibility.value,
                "expected_execution": case.expected_execution,
                "execution_eligibility": assessment.execution.value,
                "axis_scores": scores,
                "findings_exact_match": findings_match(case, assessment.finding_names),
                "result": "PASS" if (
                    scores["re_evaluation_correctness"] == "PASS"
                    and findings_match(case, assessment.finding_names)
                ) else "FAIL",
                "reason": assessment.reason,
                "note": case.note,
            }
        )
    return rows


def run_t50():
    gate = ReEvaluationGate()
    path_a = reuse_directly(T50_RECORD)
    path_b = gate.assess(T50_RECORD, T50_PRESENT)

    a_ok = path_a.value == T50_EXPECTED["A"]["expected_output"]
    b_ok = (
        path_b.eligibility.value in T50_EXPECTED["B"]["expected_eligibility"]
        and path_b.execution.value == T50_EXPECTED["B"]["expected_execution"]
    )
    return {
        "case_id": "T50-TIM-REUSE",
        "path_A": {
            "description": T50_EXPECTED["A"]["description"],
            "output": path_a.value,
            "comparisons_performed": 0,
            "legitimacy": T50_EXPECTED["A"]["legitimacy"],
            "axis_scores": T50_EXPECTED["A"]["axes"],
            "behaved_as_predicted": a_ok,
            "note": T50_EXPECTED["A"]["note"],
        },
        "path_B": {
            "description": T50_EXPECTED["B"]["description"],
            "eligibility": path_b.eligibility.value,
            "execution": path_b.execution.value,
            "findings": path_b.finding_names,
            "comparisons_performed": 4,
            "axis_scores": {
                "evidence_preservation": "PASS" if "EVIDENCE_CHANGED" in path_b.finding_names else "FAIL",
                "temporal_validity": "PASS" if "TEMPORAL_EXPIRED" in path_b.finding_names else "FAIL",
                "authority_continuity": "PASS" if "AUTHORITY_CHANGED" in path_b.finding_names else "FAIL",
                "context_continuity": "PASS" if "CONTEXT_MISMATCH" in path_b.finding_names else "FAIL",
                "re_evaluation_correctness": "PASS" if b_ok else "FAIL",
            },
            "reason": path_b.reason,
            "note": T50_EXPECTED["B"]["note"],
        },
        "comparison": {
            "A_yields": path_a.value,
            "B_yields": "%s / %s" % (path_b.eligibility.value, path_b.execution.value),
            "verdict": "A reaches ALLOW without inspecting the present. "
                       "That output is not counted as a legitimate ALLOW.",
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Tim-MoCKA comparative test runner")
    parser.add_argument("--json", default=DEFAULT_JSON)
    args = parser.parse_args(argv)

    rows = run_matrix()
    t50 = run_t50()

    if not os.path.isdir(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
    with open(args.json, "w", encoding="utf-8") as handle:
        json.dump({"matrix": rows, "critical_test": t50}, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    for row in rows:
        print(
            "%-5s %-4s past=%-14s now=%-22s -> %-12s %-8s %s"
            % (
                row["case_id"],
                row["result"],
                row["past_decision"],
                row["present_state"],
                row["actual_eligibility"],
                row["execution_eligibility"],
                ",".join(row["findings"]),
            )
        )

    print()
    print("T50-TIM-REUSE")
    print("  A (direct reuse)   : output=%s  comparisons=%d  %s"
          % (t50["path_A"]["output"], t50["path_A"]["comparisons_performed"],
             t50["path_A"]["legitimacy"]))
    print("  B (re-evaluated)   : %s / %s  comparisons=%d"
          % (t50["path_B"]["eligibility"], t50["path_B"]["execution"],
             t50["path_B"]["comparisons_performed"]))
    print("  B findings         : %s" % ", ".join(t50["path_B"]["findings"]))

    failed = [r for r in rows if r["result"] == "FAIL"]
    executed = [r for r in rows if r["execution_eligibility"] == "EXECUTE"]
    print()
    print("%d case(s), %d pass, %d fail, %d reached EXECUTE (%s)"
          % (len(rows), len(rows) - len(failed), len(failed), len(executed),
             ", ".join(r["case_id"] for r in executed) or "none"))

    spurious = [r["case_id"] for r in rows if not r["findings_exact_match"]]
    print("false-positive guard: %d/%d cases raised exactly the declared findings%s"
          % (len(rows) - len(spurious), len(rows),
             "" if not spurious else " (mismatch: %s)" % ", ".join(spurious)))

    tally = {}
    for row in rows:
        for axis, score in row["axis_scores"].items():
            tally.setdefault(axis, {}).setdefault(score, 0)
            tally[axis][score] += 1
    print()
    print("axis tally over the 10 matrix cases:")
    for axis in AXES:
        counts = tally.get(axis, {})
        print("  %-28s %s" % (axis, "  ".join("%s=%d" % kv for kv in sorted(counts.items()))))
    print()
    print("results json: %s" % args.json)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
