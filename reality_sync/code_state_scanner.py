# -*- coding: utf-8 -*-
"""Code State Scanner (Phase 4-2 Reality Sync Layer)

役割: repo全体の「現実」を取得する。
- ファイル存在確認
- syntax check (ast.parse)
- import可否確認 (IMPORT_TARGETS のみ)

推測・判定は行わない。事実(evidence)のみを CodeStateEntry に詰める。
"""

import ast
import subprocess
import sys
from pathlib import Path

from reality_sync.sync_registry import REPO_ROOT, WATCHED_FILES, IMPORT_TARGETS
from reality_sync.sync_result_model import CodeStateEntry


def _check_syntax(abs_path: Path) -> tuple[bool, str]:
    """ast.parse による構文チェック。BOM等は utf-8-sig で吸収を試みる。"""
    raw = abs_path.read_bytes()
    for enc in ("utf-8-sig", "utf-8"):
        try:
            ast.parse(raw.decode(enc))
            return True, f"AST_PARSE_OK(encoding={enc})"
        except SyntaxError as e:
            last_err = f"AST_PARSE_ERROR(encoding={enc}): line {e.lineno}: {e.msg}"
        except UnicodeDecodeError as e:
            last_err = f"DECODE_ERROR(encoding={enc}): {e}"
    return False, last_err


def _check_import(module_path: str) -> tuple[bool, str]:
    """subprocess で `python -c "import <module>"` を実行し import 可否を確認する。"""
    proc = subprocess.run(
        [sys.executable, "-c", f"import {module_path}"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.returncode == 0:
        return True, "IMPORT_OK"
    stderr_last = proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else "unknown error"
    return False, f"IMPORT_ERROR: {stderr_last}"


def scan() -> list[CodeStateEntry]:
    """WATCHED_FILES 全件を走査し CodeStateSnapshot (list[CodeStateEntry]) を返す。"""
    snapshot: list[CodeStateEntry] = []

    for rel_path in WATCHED_FILES:
        abs_path = REPO_ROOT / rel_path

        if not abs_path.exists():
            snapshot.append(CodeStateEntry(
                file_path=rel_path,
                exists=False,
                syntax_valid=None,
                import_ok=None,
                evidence="FILE_NOT_FOUND",
            ))
            continue

        syntax_valid, syntax_evidence = _check_syntax(abs_path)

        import_ok = None
        import_evidence = ""
        if rel_path in IMPORT_TARGETS:
            import_ok, import_evidence = _check_import(IMPORT_TARGETS[rel_path])

        evidence = syntax_evidence
        if import_evidence:
            evidence += " | " + import_evidence

        snapshot.append(CodeStateEntry(
            file_path=rel_path,
            exists=True,
            syntax_valid=syntax_valid,
            import_ok=import_ok,
            evidence=evidence,
        ))

    return snapshot


if __name__ == "__main__":
    for entry in scan():
        print(entry)
