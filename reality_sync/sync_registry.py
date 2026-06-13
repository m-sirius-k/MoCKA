# -*- coding: utf-8 -*-
"""Sync Registry (Phase 4-2 Reality Sync Layer)

truth_rules / validation_methods / allowed evidence types / severity mapping
を一元管理する。ここに定義されないルールは Sync Engine では使用しない。
"""

from pathlib import Path

# このリポジトリのルート
REPO_ROOT = Path("C:/Users/sirok/MoCKA")

# --- Truth Rules -----------------------------------------------------------
# "FIXED" と認定してよい唯一の条件:
#   syntax_valid == True かつ import_ok != False (Noneも許容: importチェック対象外ファイル)
# それ以外は全て "BROKEN"
TRUTH_RULE = {
    "fixed_requires": ["syntax_valid"],
    "fixed_optional": ["import_ok"],
    "default_status": "BROKEN",
}

# --- Validation Methods (許可される検証手段) --------------------------------
ALLOWED_VALIDATION_METHODS = [
    "ast_parse",        # syntax check
    "module_import",    # import実行
    "unit_test",        # pytest等のPASS結果
    "lint",             # lintツールのPASS結果
    "runtime_execution",  # 実行ログ
]

# --- Evidence Types ----------------------------------------------------------
ALLOWED_EVIDENCE_TYPES = [
    "AST_PARSE_OK",
    "AST_PARSE_ERROR",
    "IMPORT_OK",
    "IMPORT_ERROR",
    "FILE_NOT_FOUND",
    "REPORT_QUOTE",
]

# --- Severity Mapping ---------------------------------------------------------
# discrepancy_type -> severity
SEVERITY_MAP = {
    "NONE": "NONE",
    "FALSE_FIXED": "CRITICAL",   # レポートが「修正済み」と主張、実際はBROKEN
    "FALSE_BROKEN": "LOW",        # レポートが「未修正/FAIL」、実際はFIXED (過剰報告、実害小)
    "MISSING_FIX": "HIGH",        # レポートに記載なし、実際はBROKEN
    "REVERSED": "CRITICAL",       # 報告と実態が完全に逆転
    "NO_CLAIM": "NONE",           # レポート言及なし、実際はFIXED (問題なし)
}

# --- 監視対象ファイル (Code State Scanner の走査対象) -------------------------
# entrypoint / 既存follow-upレポートで言及された対象を中心に登録
WATCHED_FILES = [
    "app.py",
    "main.py",
    "mocka_mcp_server.py",
    "interface/router.py",
    "interface/auto_gate.py",
    "interface/health_check.py",
    "interface/tech_watcher.py",
    "interface/incident_learner.py",
    "interface/morphology_engine.py",
    "interface/cross_audit.py",
    "interface/Essence_Direct_Parser.py",
    "interface/essence_pipeline.py",
    "interface/essence_auto_updater.py",
    "interface/language_detector.py",
    "interface/simulation_layer.py",
    "caliber/chat_pipeline/mocka_caliber_server.py",
    "runtime/main_loop.py",
    "runtime/civilization_bridge.py",
    "runtime/action_executor.py",
    "structural/bee.py",
    "structural/beta_engine.py",
    "scripts/ledger/ledger_verify.py",
    "scripts/ledger/anchor_update.py",
]

# --- importチェックを行うファイル (パッケージ経由でimport可能なもののみ) -------
# file_path -> import module path
IMPORT_TARGETS = {
    "interface/router.py": "interface.router",
    "main.py": "main",
    "runtime/action_executor.py": "runtime.action_executor",
}

# --- 監査対象レポート --------------------------------------------------------
REPORT_FILES = [
    "PlanningCaliber/fp/mocka30_architecture_review_20260613.md",
    "PlanningCaliber/fp/mocka30_followup_audit_20260613.md",
]
