# -*- coding: utf-8 -*-
"""Report Evidence Linker (Phase 4-3 Report Truth Governance Layer)

役割: code_state_scanner / reality_sync.sync_engine の結果を
ファイルパス単位の Evidence にマッピングする。
claim -> evidence の対応付けは行うが、判定(FIXED/BROKEN)は行わない
(判定はTruthValidatorの専属)。
"""

from reality_sync.code_state_scanner import scan
from reality_sync.truth_checker import determine_truth
from report_truth_governance.report_claim_model import Evidence


def link() -> dict:
    """file_path -> list[Evidence] の辞書を返す。

    Evidence.source:
      - "code_state_scanner" : ast.parse / import 結果そのもの
      - "reality_sync.sync_engine" : TruthCheckerによる確定状態 (Reality Sync Result)
    """
    evidence_map: dict = {}

    snapshot = scan()
    for entry in snapshot:
        status, detail = determine_truth(entry)

        evidence_map.setdefault(entry.file_path, []).append(Evidence(
            file_path=entry.file_path,
            source="code_state_scanner",
            status=status,
            detail=entry.evidence,
        ))

        evidence_map[entry.file_path].append(Evidence(
            file_path=entry.file_path,
            source="reality_sync.sync_engine",
            status=status,
            detail=detail,
        ))

    return evidence_map


if __name__ == "__main__":
    for path, evs in link().items():
        for e in evs:
            print(e)
