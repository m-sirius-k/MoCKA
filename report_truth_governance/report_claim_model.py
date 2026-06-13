# -*- coding: utf-8 -*-
"""Report Truth Governance - Data Models (Phase 4-3)

このモジュールはデータ構造のみを定義する。判定ロジックは持たない。
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ReportClaim:
    """1レポートの1行から抽出された主張"""
    file_path: str
    report_source: str        # レポートファイル名 (相対パス)
    line_no: int
    claimed_status: str        # "FIXED" / "BROKEN" / "UNKNOWN"
    quote: str


@dataclass
class ReportClaimSet:
    """全レポートから抽出された ReportClaim の集合"""
    claims: list = field(default_factory=list)  # list[ReportClaim]

    def for_file(self, file_path: str) -> list:
        return [c for c in self.claims if c.file_path == file_path]

    def files(self) -> set:
        return {c.file_path for c in self.claims}


@dataclass
class Evidence:
    """code_state_scanner / reality_sync 由来の証拠"""
    file_path: str
    source: str                 # "code_state_scanner" / "reality_sync.sync_engine" / "test_execution"
    status: str                  # "FIXED" / "BROKEN"
    detail: str                  # evidence文字列 (AST_PARSE_ERROR等)


@dataclass
class Conflict:
    """検出された矛盾"""
    file_path: str
    conflict_type: str           # "INTRA_REPORT" / "INTER_REPORT" / "CLAIM_VS_TRUTH" / "OUTDATED_CLAIM"
    description: str
    involved_sources: list = field(default_factory=list)
    resolved: bool = False
    resolution: str = ""


@dataclass
class ReportTruthState:
    """Pipeline最終出力"""
    file_path: str
    claim_state: str             # レポート群が主張する状態 (複数あれば結合表記)
    truth_state: str              # TruthValidatorが確定した状態 (FIXED/BROKEN)
    conflict_flag: bool
    evidence: str
    resolution_action: str
    confidence_score: float       # 0.0 - 1.0
    conflicts: list = field(default_factory=list)  # list[Conflict]
