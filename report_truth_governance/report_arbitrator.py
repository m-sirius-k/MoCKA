# -*- coding: utf-8 -*-
"""Report Arbitrator (Phase 4-3 Report Truth Governance Layer)

役割: Conflict を解消する。Conflictそのものを消去するのではなく、
各Conflictに resolution (解決方法の記述) と resolved フラグを付与する。

優先順位 (絶対):
    1. Code Evidence            (code_state_scanner: ast.parse / import)
    2. Reality Sync Result      (reality_sync.sync_engine の確定 actual_status)
    3. Test Execution Result    (本実装ではunit_test evidenceが存在する場合のみ)
    4. Report Claim             (最下位。常に上位3つに従う)

このモジュールはレポートを上書きしない。Conflict.resolution に
「何が優先され、どう解決されたか」を記述するのみ。
"""

from report_truth_governance.report_claim_model import Conflict


PRIORITY_ORDER = [
    "code_state_scanner",       # 1. Code Evidence
    "reality_sync.sync_engine",  # 2. Reality Sync Result
    "test_execution",            # 3. Test Execution Result
    # 4. Report Claim は evidence_map に存在しないため自動的に最下位
]


def arbitrate(conflict: Conflict, evidence_map: dict, truth_state: str) -> Conflict:
    """Conflict を解消し、resolved=True と resolution文字列を設定した
    新しいConflictを返す(入力は変更しない)。

    全てのConflict種別について、最終的な状態は必ず truth_state
    (= Code Evidence -> Reality Sync Result の順で確定済み) を採用する。
    Report Claim は採用されない(常に最下位)。
    """
    evs = evidence_map.get(conflict.file_path, [])
    winning_evidence = None
    for source in PRIORITY_ORDER:
        match = next((e for e in evs if e.source == source), None)
        if match is not None:
            winning_evidence = match
            break

    evidence_desc = (
        f"{winning_evidence.source}={winning_evidence.status} ({winning_evidence.detail})"
        if winning_evidence is not None else "NO_EVIDENCE"
    )

    if conflict.conflict_type == "INTRA_REPORT":
        resolution = (
            f"内部矛盾を含む report_source={conflict.involved_sources} の claim は"
            f"無効とし、優先順位最上位の証拠 [{evidence_desc}] を採用。"
            f"確定状態 = {truth_state}"
        )
    elif conflict.conflict_type == "INTER_REPORT":
        resolution = (
            f"レポート間の不一致 {conflict.involved_sources} は Report Claim (最下位優先)"
            f"のため採用せず、優先順位最上位の証拠 [{evidence_desc}] を採用。"
            f"確定状態 = {truth_state}"
        )
    elif conflict.conflict_type == "CLAIM_VS_TRUTH":
        resolution = (
            f"Report Claim と Code Evidence/Reality Sync Result が不一致のため、"
            f"優先順位に従い [{evidence_desc}] を採用。"
            f"確定状態 = {truth_state} (Report Claimは不採用)"
        )
    elif conflict.conflict_type == "OUTDATED_CLAIM":
        resolution = (
            f"{conflict.involved_sources} のFIXED主張は陳腐化(outdated)と判定。"
            f"優先順位最上位の証拠 [{evidence_desc}] により確定状態 = {truth_state}"
        )
    else:
        resolution = f"未知のconflict_type。優先順位最上位の証拠 [{evidence_desc}] を採用。確定状態 = {truth_state}"

    return Conflict(
        file_path=conflict.file_path,
        conflict_type=conflict.conflict_type,
        description=conflict.description,
        involved_sources=conflict.involved_sources,
        resolved=True,
        resolution=resolution,
    )


if __name__ == "__main__":
    from report_truth_governance.report_parser import parse
    from report_truth_governance.report_evidence_linker import link
    from report_truth_governance.report_conflict_detector import detect
    from report_truth_governance.report_truth_validator import true_state

    claim_set = parse()
    evidence_map = link()

    for file_path in sorted(claim_set.files()):
        truth, _ = true_state(file_path, evidence_map)
        for c in detect(file_path, claim_set, truth):
            print(arbitrate(c, evidence_map, truth))
