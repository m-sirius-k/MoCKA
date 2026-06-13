# -*- coding: utf-8 -*-
"""Report Pipeline (Phase 4-3 Report Truth Governance Layer) - CLI Entrypoint

usage:
    python -m report_truth_governance.report_pipeline

処理フロー:
    Report(s)
       v
    Report Parser
       v
    Evidence Linker
       v
    Conflict Detector
       v
    Truth Validator
       v
    Arbitrator
       v
    Alignment Engine
       v
    Governance Engine
       v
    ReportTruthState
"""

from report_truth_governance.report_parser import parse
from report_truth_governance.report_evidence_linker import link
from report_truth_governance.report_conflict_detector import detect
from report_truth_governance.report_truth_validator import true_state
from report_truth_governance.report_arbitrator import arbitrate
from report_truth_governance.report_alignment_engine import generate
from report_truth_governance.report_governance_engine import govern


def run():
    """Returns (results: list[ReportTruthState], statuses: dict[file_path -> 'PASS'/'FAIL'],
    alignment_diffs: dict[file_path -> list[AlignmentDiff]])
    """
    claim_set = parse()
    evidence_map = link()

    results = []
    statuses = {}
    alignment_diffs = {}

    for file_path in sorted(claim_set.files()):
        truth, evidence = true_state(file_path, evidence_map)

        raw_conflicts = detect(file_path, claim_set, truth)
        resolved_conflicts = [arbitrate(c, evidence_map, truth) for c in raw_conflicts]

        diffs = generate(file_path, claim_set, truth)
        alignment_diffs[file_path] = diffs

        state, status = govern(file_path, claim_set, evidence_map, truth, evidence, resolved_conflicts)

        results.append(state)
        statuses[file_path] = status

    return results, statuses, alignment_diffs


def _print_results(results, statuses, alignment_diffs):
    print("=" * 100)
    print("REPORT TRUTH STATE")
    print("=" * 100)
    header = f"{'file_path':<45} {'claim_state':<14} {'truth_state':<8} {'conflict':<8} {'confidence':<10} {'gov_status'}"
    print(header)
    print("-" * 100)
    for r in results:
        print(f"{r.file_path:<45} {r.claim_state:<14} {r.truth_state:<8} "
              f"{str(r.conflict_flag):<8} {r.confidence_score:<10} {statuses[r.file_path]}")

    print()
    print("=" * 100)
    print("CONFLICTS (resolved)")
    print("=" * 100)
    any_conflict = False
    for r in results:
        for c in r.conflicts:
            any_conflict = True
            print(f"- [{r.file_path}] {c.conflict_type}")
            print(f"    desc      : {c.description}")
            print(f"    resolved  : {c.resolved}")
            print(f"    resolution: {c.resolution}")
    if not any_conflict:
        print("検出された矛盾なし。")

    print()
    print("=" * 100)
    print("ALIGNMENT DIFFS (修正案 / レポート未変更)")
    print("=" * 100)
    any_diff = False
    for file_path, diffs in alignment_diffs.items():
        for d in diffs:
            any_diff = True
            print(f"- {d.diff_description}")
            print(f"    {d.proposed_correction}")
    if not any_diff:
        print("差分なし。")

    print()
    fail_files = [f for f, s in statuses.items() if s == "FAIL"]
    print("=" * 100)
    print(f"GOVERNANCE OVERALL: {'FAIL' if fail_files else 'PASS'}")
    if fail_files:
        print(f"  unresolved conflict files: {fail_files}")
    print("=" * 100)


def main():
    results, statuses, alignment_diffs = run()
    _print_results(results, statuses, alignment_diffs)


if __name__ == "__main__":
    main()
