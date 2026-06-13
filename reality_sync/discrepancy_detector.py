# -*- coding: utf-8 -*-
"""Discrepancy Detector (Phase 4-2 Reality Sync Layer)

役割: ReportClaim (報告された状態) と actual_status (TruthCheckerが確定した
コードの現実) を比較し、discrepancy_type を分類する。

分類:
  NONE          - 報告と実態が一致 (FIXED==FIXED, BROKEN==BROKEN)
  FALSE_FIXED   - 報告は FIXED だが実態は BROKEN (最重要: 自己欺瞞)
  FALSE_BROKEN  - 報告は BROKEN だが実態は FIXED (過剰報告)
  MISSING_FIX   - レポートに言及なし、実態は BROKEN
  NO_CLAIM      - レポートに言及なし、実態は FIXED (問題なし)
  REVERSED      - 同一ファイルに対して複数レポートが矛盾する claimed_status を
                   出している場合 (報告間の矛盾そのもの)
"""

from reality_sync.sync_result_model import ReportClaim


def detect(file_path: str, actual_status: str, claims: list[ReportClaim]) -> tuple[str, str, list]:
    """指定ファイルについて discrepancy_type と reported_status, sources を返す。

    Returns:
        (discrepancy_type, reported_status, sources)
    """
    file_claims = [c for c in claims if c.file_path == file_path]

    if not file_claims:
        if actual_status == "BROKEN":
            return "MISSING_FIX", "NO_CLAIM", []
        return "NO_CLAIM", "NO_CLAIM", []

    statuses = {c.claimed_status for c in file_claims if c.claimed_status != "UNKNOWN"}
    sources = [c.report_source for c in file_claims]

    if len(statuses) > 1:
        # 複数レポート間で主張が矛盾 (例: 一方はFIXED、他方はBROKEN)
        reported_status = "/".join(sorted(statuses))
        return "REVERSED", reported_status, sources

    if not statuses:
        reported_status = "UNKNOWN"
        if actual_status == "BROKEN":
            return "MISSING_FIX", reported_status, sources
        return "NO_CLAIM", reported_status, sources

    reported_status = statuses.pop()

    if reported_status == actual_status:
        return "NONE", reported_status, sources

    if reported_status == "FIXED" and actual_status == "BROKEN":
        return "FALSE_FIXED", reported_status, sources

    if reported_status == "BROKEN" and actual_status == "FIXED":
        return "FALSE_BROKEN", reported_status, sources

    return "NONE", reported_status, sources


if __name__ == "__main__":
    from reality_sync.report_state_validator import validate

    claims = validate()
    print(detect("interface/router.py", "BROKEN", claims))
