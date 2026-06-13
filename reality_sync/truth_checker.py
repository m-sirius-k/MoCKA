# -*- coding: utf-8 -*-
"""Truth Checker (Phase 4-2 Reality Sync Layer)

唯一の真実判定レイヤー。
CodeStateEntry のみを入力とし、TRUTH_RULE に基づいて
"FIXED" / "BROKEN" を確定する。レポートの主張は一切参照しない。

ルール (sync_registry.TRUTH_RULE):
  syntax_valid == True  -> FIXED (import_okが定義されていてFalseの場合はBROKEN)
  それ以外               -> BROKEN
"""

from reality_sync.sync_result_model import CodeStateEntry


def determine_truth(entry: CodeStateEntry) -> tuple[str, str]:
    """CodeStateEntry から (actual_status, evidence) を返す。

    - exists == False                -> BROKEN (FILE_NOT_FOUND)
    - syntax_valid == False           -> BROKEN
    - syntax_valid == True かつ import_ok == False -> BROKEN
    - syntax_valid == True かつ (import_ok in (True, None)) -> FIXED
    """
    if not entry.exists:
        return "BROKEN", "FILE_NOT_FOUND"

    if entry.syntax_valid is not True:
        return "BROKEN", entry.evidence

    if entry.import_ok is False:
        return "BROKEN", entry.evidence

    return "FIXED", entry.evidence


if __name__ == "__main__":
    from reality_sync.code_state_scanner import scan

    for e in scan():
        status, evidence = determine_truth(e)
        print(f"{e.file_path}: {status} ({evidence})")
