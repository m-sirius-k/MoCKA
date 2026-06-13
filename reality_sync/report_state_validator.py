# -*- coding: utf-8 -*-
"""Report State Validator (Phase 4-2 Reality Sync Layer)

役割: 既存レポート(Markdown)を解析し、ファイルごとの「修正済み/未修正」主張を
ReportClaim として抽出する。レポートの記述を真実とはみなさない
(あくまで「何を主張しているか」の事実抽出)。

抽出方法:
  各 WATCHED_FILES の file_path (例: "interface/router.py") が言及されている行を探し、
  その行および前後の文脈から FIXED / BROKEN / UNKNOWN を判定するキーワードを照合する。
"""

import re
from pathlib import Path

from reality_sync.sync_registry import REPO_ROOT, WATCHED_FILES, REPORT_FILES
from reality_sync.sync_result_model import ReportClaim

# レポート文中で「修正済み」を意味するキーワード
FIXED_KEYWORDS = [
    "修正済み", "PASS", "FIXED", "解決済み", "完了",
]

# レポート文中で「未修正/問題あり」を意味するキーワード
BROKEN_KEYWORDS = [
    "未修正", "FAIL", "BROKEN", "存在する", "syntax error", "SyntaxError",
    "構文エラー", "未確認",
]


def _classify_line(line: str) -> str:
    """1行のテキストから FIXED / BROKEN / UNKNOWN を判定する。
    両方のキーワードが存在する場合は BROKEN を優先する
    (例: '「修正済み」と記載されているが実際はFAIL' のような訂正記述を取りこぼさないため)。
    """
    has_broken = any(k in line for k in BROKEN_KEYWORDS)
    has_fixed = any(k in line for k in FIXED_KEYWORDS)

    if has_broken:
        return "BROKEN"
    if has_fixed:
        return "FIXED"
    return "UNKNOWN"


def validate() -> list[ReportClaim]:
    """REPORT_FILES を走査し、WATCHED_FILES に対応する ReportClaim 一覧を返す。"""
    claims: list[ReportClaim] = []

    for report_rel in REPORT_FILES:
        report_path = REPO_ROOT / report_rel
        if not report_path.exists():
            continue

        text = report_path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()

        for rel_path in WATCHED_FILES:
            # ファイルパスの表記揺れ対応: "interface/router.py" と "interface\router.py" 等
            patterns = [rel_path, rel_path.replace("/", "\\")]
            basename = Path(rel_path).name

            for i, line in enumerate(lines):
                hit = any(p in line for p in patterns) or basename in line
                if not hit:
                    continue

                status = _classify_line(line)

                # ヒット行だけで UNKNOWN の場合、直後数行も確認 (テーブル形式対策)
                if status == "UNKNOWN":
                    for j in range(i + 1, min(i + 3, len(lines))):
                        status = _classify_line(lines[j])
                        if status != "UNKNOWN":
                            line = line + " / " + lines[j]
                            break

                claims.append(ReportClaim(
                    file_path=rel_path,
                    report_source=report_rel,
                    claimed_status=status,
                    quote=line.strip()[:300],
                ))

    return claims


if __name__ == "__main__":
    for c in validate():
        print(c)
