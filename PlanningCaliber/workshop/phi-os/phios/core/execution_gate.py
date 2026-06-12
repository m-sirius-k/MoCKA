# phi_os/core/execution_gate.py
"""verify_all.py をゲートとして実行し、危険操作の前提条件とする"""
from __future__ import annotations

import functools
import subprocess
import sys
from pathlib import Path

_MOCKA_ROOT = Path(__file__).resolve().parents[5]
VERIFY_ALL_PATH = _MOCKA_ROOT / "verify_all.py"


def gate_check() -> bool:
    """verify_all.pyを実行し、ALL CHECKS PASSEDならTrueを返す"""
    result = subprocess.run(
        [sys.executable, str(VERIFY_ALL_PATH)],
        capture_output=True, text=True, cwd=str(_MOCKA_ROOT),
    )
    return result.returncode == 0 and "ALL CHECKS PASSED" in result.stdout


def require_gate(func):
    """gate_check()がFalseの場合RuntimeErrorを発生させるデコレータ"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not gate_check():
            raise RuntimeError(f"execution_gate blocked: verify_all failed before '{func.__name__}'")
        return func(*args, **kwargs)
    return wrapper
