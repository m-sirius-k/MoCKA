# -*- coding: utf-8 -*-
"""Report Truth Validator (Phase 4-3 Report Truth Governance Layer)

ルール:
    IF code_evidence == PASS:
        TRUE_STATE = FIXED
    ELSE:
        TRUE_STATE = BROKEN

レポートのclaimは一切参照しない。判定は report_evidence_linker が提供する
"reality_sync.sync_engine" Evidence (= reality_sync.truth_checker の確定結果)
にのみ基づく。これにより Phase 4-2 の Truth Checker をそのまま再利用し、
判定ロジックの二重実装を避ける。
"""

from report_truth_governance.report_claim_model import Evidence


def true_state(file_path: str, evidence_map: dict) -> tuple:
    """(truth_state, evidence_detail) を返す。

    code_state_scanner / reality_sync.sync_engine の両Evidenceが存在しない
    file_pathに対しては BROKEN (NO_EVIDENCE) を返す(推測禁止のため、
    証拠がない=安全側に倒す)。
    """
    evs = evidence_map.get(file_path, [])

    sync_ev = next((e for e in evs if e.source == "reality_sync.sync_engine"), None)
    if sync_ev is None:
        return "BROKEN", "NO_EVIDENCE"

    if sync_ev.status == "FIXED":
        return "FIXED", sync_ev.detail

    return "BROKEN", sync_ev.detail


if __name__ == "__main__":
    from report_truth_governance.report_evidence_linker import link

    evidence_map = link()
    for file_path in evidence_map:
        print(file_path, "->", true_state(file_path, evidence_map))
