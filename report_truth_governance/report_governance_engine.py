# -*- coding: utf-8 -*-
"""Report Governance Engine (Phase 4-3 Report Truth Governance Layer)

統治核。制約:
  - report override 禁止   : レポートのファイルを書き換えない
  - truth override 禁止     : Arbitratorが確定したtruth_stateを上書きしない
  - conflict未解決状態はFAIL : Conflict.resolved == False が1件でもあれば
                                governance_status = "FAIL"

このモジュールは ReportTruthState を構築する最終段。
confidence_score は以下のルールで算出する(推測ではなく機械的計算):
  - base = 1.0
  - evidence == "NO_EVIDENCE" の場合 base = 0.3
  - conflictが1件ある毎に -0.15 (下限0.0)
  - 全conflictが resolved == True であることを確認 (未解決があればgovernance FAIL)
"""

from report_truth_governance.report_claim_model import ReportTruthState


def govern(file_path: str, claim_set, evidence_map: dict, truth_state: str,
           truth_evidence: str, conflicts: list) -> tuple:
    """ReportTruthState と governance_status ("PASS"/"FAIL") を返す。"""

    claims = claim_set.for_file(file_path)
    meaningful = {c.claimed_status for c in claims if c.claimed_status != "UNKNOWN"}
    claim_state = "/".join(sorted(meaningful)) if meaningful else "NO_CLAIM"

    conflict_flag = len(conflicts) > 0

    unresolved = [c for c in conflicts if not c.resolved]
    governance_status = "FAIL" if unresolved else "PASS"

    if conflicts:
        resolution_action = "; ".join(c.resolution for c in conflicts if c.resolved)
        if unresolved:
            resolution_action += " | UNRESOLVED CONFLICTS PRESENT"
    else:
        resolution_action = "差分なし。レポート記述はCode Evidenceと一致。"

    base = 1.0
    if truth_evidence == "NO_EVIDENCE":
        base = 0.3
    confidence = max(0.0, base - 0.15 * len(conflicts))

    state = ReportTruthState(
        file_path=file_path,
        claim_state=claim_state,
        truth_state=truth_state,
        conflict_flag=conflict_flag,
        evidence=truth_evidence,
        resolution_action=resolution_action,
        confidence_score=round(confidence, 2),
        conflicts=conflicts,
    )

    return state, governance_status


if __name__ == "__main__":
    from report_truth_governance.report_parser import parse
    from report_truth_governance.report_evidence_linker import link
    from report_truth_governance.report_conflict_detector import detect
    from report_truth_governance.report_truth_validator import true_state
    from report_truth_governance.report_arbitrator import arbitrate

    claim_set = parse()
    evidence_map = link()

    for file_path in sorted(claim_set.files()):
        truth, evidence = true_state(file_path, evidence_map)
        raw_conflicts = detect(file_path, claim_set, truth)
        resolved = [arbitrate(c, evidence_map, truth) for c in raw_conflicts]
        state, status = govern(file_path, claim_set, evidence_map, truth, evidence, resolved)
        print(status, state)
