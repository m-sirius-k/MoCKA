# -*- coding: utf-8 -*-
"""Sync Result Model (Phase 4-2 Reality Sync Layer)

データ構造のみを定義する。判定ロジックは持たない。
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CodeStateEntry:
    """1ファイルに対するコード現実状態"""
    file_path: str
    exists: bool
    syntax_valid: Optional[bool] = None   # ast.parse 成功 = True
    import_ok: Optional[bool] = None      # モジュールimport成功 = True
    evidence: str = ""                    # 検証コマンド/エラー内容(EVIDENCE_ONLY)


@dataclass
class ReportClaim:
    """既存レポートが主張している状態"""
    file_path: str
    report_source: str       # レポートファイル名
    claimed_status: str      # "FIXED" / "BROKEN" / "UNKNOWN"
    quote: str                # 根拠となったレポート本文の抜粋


@dataclass
class SyncResult:
    """1ファイルに対する最終同期結果"""
    file_path: str
    reported_status: str          # ReportClaim.claimed_status (複数あれば結合)
    actual_status: str             # TruthChecker が確定した状態 "FIXED" / "BROKEN"
    discrepancy_type: str          # NONE / FALSE_FIXED / FALSE_BROKEN / MISSING_FIX / REVERSED / NO_CLAIM
    severity: str                   # NONE / LOW / MEDIUM / HIGH / CRITICAL
    fix_required: bool
    evidence: str = ""
    sources: list = field(default_factory=list)  # 参照したレポートファイル一覧
