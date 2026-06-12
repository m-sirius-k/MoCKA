"""Verification v1

Decision LedgerのSHA-256チェーンを外部から検証するための薄いラッパー。
ISEの他モジュールに依存せず、decision_ledger単体で動作する。
"""
from __future__ import annotations

from ise.decision_ledger import read_ledger, verify_chain


def verify() -> dict:
    """
    Decision Ledgerのチェーン整合性を検証する。
    戻り値は /api/verification/verify のレスポンス本体として使える形式。
    """
    ok, message = verify_chain()
    return {
        "verified": ok,
        "message": message,
        "entry_count": len(read_ledger()),
    }
