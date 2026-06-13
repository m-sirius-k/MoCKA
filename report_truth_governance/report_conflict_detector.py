# -*- coding: utf-8 -*-
"""Report Conflict Detector (Phase 4-3 Report Truth Governance Layer)

検出対象:
  - INTRA_REPORT  : 同一レポート内で同一ファイルに対する claim が
                     FIXED と BROKEN の両方を含む(内部矛盾)
  - INTER_REPORT  : 複数レポート間で同一ファイルの claim が一致しない
  - CLAIM_VS_TRUTH: claim (集約結果) と truth_state (コード由来) が不一致
  - OUTDATED_CLAIM: claimed_status == FIXED だが truth_state == BROKEN
                     かつ該当レポートが他レポートより古い場合
                     (本実装ではタイムスタンプ情報がレポート本文にないため、
                      REPORT_FILES のリスト順=新しい順という前提を明示した上で
                      "古いレポートの単独FIXED主張" のみを対象とする)

矛盾は検出するのみで、解決は report_arbitrator.py が行う。
"""

from report_truth_governance.report_claim_model import Conflict


def detect(file_path: str, claim_set, truth_state: str) -> list:
    """指定ファイルについて Conflict のリストを返す。"""
    conflicts = []
    file_claims = [c for c in claim_set.claims if c.file_path == file_path]

    if not file_claims:
        return conflicts

    # --- INTRA_REPORT: レポートごとに statuses を集計 ---
    by_report: dict = {}
    for c in file_claims:
        by_report.setdefault(c.report_source, set()).add(c.claimed_status)

    for report_source, statuses in by_report.items():
        meaningful = statuses - {"UNKNOWN"}
        if len(meaningful) > 1:
            conflicts.append(Conflict(
                file_path=file_path,
                conflict_type="INTRA_REPORT",
                description=f"{report_source} 内で {file_path} に対する claim が "
                            f"{sorted(meaningful)} の両方を含む(内部矛盾)",
                involved_sources=[report_source],
            ))

    # --- INTER_REPORT: レポート間で代表statusが異なる ---
    report_repr_status: dict = {}
    for report_source, statuses in by_report.items():
        meaningful = statuses - {"UNKNOWN"}
        if meaningful:
            # INTRA_REPORT矛盾がある場合は代表値を確定できないため "AMBIGUOUS"
            report_repr_status[report_source] = (
                "AMBIGUOUS" if len(meaningful) > 1 else next(iter(meaningful))
            )

    distinct = {v for v in report_repr_status.values()}
    if len(distinct) > 1:
        conflicts.append(Conflict(
            file_path=file_path,
            conflict_type="INTER_REPORT",
            description=f"レポート間で {file_path} の claim が不一致: {report_repr_status}",
            involved_sources=list(report_repr_status.keys()),
        ))

    # --- CLAIM_VS_TRUTH: 集約claimとtruth_stateの不一致 ---
    meaningful_all = {c.claimed_status for c in file_claims if c.claimed_status != "UNKNOWN"}
    if len(meaningful_all) == 1:
        claim_state = next(iter(meaningful_all))
        if claim_state != truth_state:
            conflicts.append(Conflict(
                file_path=file_path,
                conflict_type="CLAIM_VS_TRUTH",
                description=f"レポートの主張({claim_state}) とコードの真実({truth_state}) が不一致",
                involved_sources=[c.report_source for c in file_claims],
            ))

    # --- OUTDATED_CLAIM: 単独レポートがFIXEDと主張、truthはBROKEN ---
    # REPORT_FILES は架構レポート→follow-upレポートの順(新しい主張ほど後ろ)。
    # 「古いレポートのみがFIXEDと主張し、新しいレポート/コードはBROKEN」場合を
    # OUTDATED_CLAIM として明示する。
    if truth_state == "BROKEN":
        for report_source, status in report_repr_status.items():
            if status == "FIXED":
                conflicts.append(Conflict(
                    file_path=file_path,
                    conflict_type="OUTDATED_CLAIM",
                    description=f"{report_source} は {file_path} を FIXED と主張しているが、"
                                 f"現在のコード状態は BROKEN (レポートは陳腐化している)",
                    involved_sources=[report_source],
                ))

    return conflicts


if __name__ == "__main__":
    from report_truth_governance.report_parser import parse
    from report_truth_governance.report_evidence_linker import link

    claim_set = parse()
    evidence_map = link()

    for file_path in sorted(claim_set.files()):
        evs = evidence_map.get(file_path, [])
        truth = next((e.status for e in evs if e.source == "reality_sync.sync_engine"), "BROKEN")
        for c in detect(file_path, claim_set, truth):
            print(c)
