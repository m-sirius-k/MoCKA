# -*- coding: utf-8 -*-
"""Report Parser (Phase 4-3 Report Truth Governance Layer)

役割: 既存レポート(Markdown)を解析し、WATCHED_FILESに対応する claim を
行番号付きで抽出する。レポートを真実とはみなさない(主張の事実抽出のみ)。
"""

from pathlib import Path

from reality_sync.sync_registry import REPO_ROOT, WATCHED_FILES, REPORT_FILES
from report_truth_governance.report_claim_model import ReportClaim, ReportClaimSet

FIXED_KEYWORDS = ["修正済み", "PASS", "FIXED", "解決済み", "完了"]
BROKEN_KEYWORDS = [
    "未修正", "FAIL", "BROKEN", "存在する", "syntax error", "SyntaxError",
    "構文エラー", "未確認",
]


def _classify_line(line: str) -> str:
    has_broken = any(k in line for k in BROKEN_KEYWORDS)
    has_fixed = any(k in line for k in FIXED_KEYWORDS)
    if has_broken:
        return "BROKEN"
    if has_fixed:
        return "FIXED"
    return "UNKNOWN"


def parse() -> ReportClaimSet:
    """REPORT_FILES を走査し ReportClaimSet を返す。"""
    claim_set = ReportClaimSet()

    for report_rel in REPORT_FILES:
        report_path = REPO_ROOT / report_rel
        if not report_path.exists():
            continue

        text = report_path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()

        for rel_path in WATCHED_FILES:
            patterns = [rel_path, rel_path.replace("/", "\\")]
            basename = Path(rel_path).name

            for i, line in enumerate(lines):
                hit = any(p in line for p in patterns) or basename in line
                if not hit:
                    continue

                status = _classify_line(line)
                merged_line = line
                line_no = i + 1

                if status == "UNKNOWN":
                    for j in range(i + 1, min(i + 3, len(lines))):
                        s2 = _classify_line(lines[j])
                        if s2 != "UNKNOWN":
                            status = s2
                            merged_line = line + " / " + lines[j]
                            break

                claim_set.claims.append(ReportClaim(
                    file_path=rel_path,
                    report_source=report_rel,
                    line_no=line_no,
                    claimed_status=status,
                    quote=merged_line.strip()[:300],
                ))

    return claim_set


if __name__ == "__main__":
    cs = parse()
    for c in cs.claims:
        print(c)
