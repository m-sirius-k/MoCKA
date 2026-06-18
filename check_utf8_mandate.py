#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MoCKA UTF-8 Check Mandate (TODO_333/TODO_338)
起動時に自動実行 - 違反があれば警告

Rule 1: open()にencoding指定なし
Rule 2: Shift-JIS系エンコーディング使用
Rule 3: PowerShell Invoke-WebRequest+Body
Rule 4: print/logging内の非ASCII装飾記号 (TODO_338)
Rule 5: CLI実行系スクリプトのreconfigure未適用 (TODO_338)
"""
import os
import sys
import re
import io
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

ROOT = Path(r"C:\Users\sirok\MoCKA")
VIOLATIONS = []

# チェック対象外ディレクトリ
SKIP_DIRS = {"__pycache__", ".git", "node_modules", "venv", ".venv", "archive"}

# Rule 5対象ディレクトリ (CLI実行系)
CLI_DIRS = {"mocka_v3_eval", "runtime", "structural", "scripts"}

# Rule 5除外: サービス常駐系ファイル名パターン（17件程度）
DAEMON_PATTERNS = {
    "main_loop", "mocka_watcher", "essence_auto_updater", "ping_generator",
    "mecab_service", "gateway", "mocka_mcp_server", "mocka_caliber_server",
    "app", "sync_watch", "risk_scorer", "risk_interpreter",
    "civilization_runtime_loop", "civilization_loop_engine",
    "civilization_heartbeat_engine", "civilization_boot_engine",
    "shadow_runtime",
}

# ==============================
# Rule 1: open()にencoding指定なし
# ==============================
OPEN_NO_ENC = re.compile(r'open\s*\([^)]+\)(?![^)]*encoding)')

# ==============================
# Rule 4: print/logging内の非ASCII装飾記号
# ==============================
# CP932で文字化けする可能性のある非ASCII装飾記号
NON_ASCII_DECORATORS = re.compile(
    r'[«»—―‘’“”'
    r'•‥…‧※←-⇿'
    r'─-╿■-◿☀-⛿'
    r'✀-➿　-〿【-〗'
    r'！-｠￠-￯'
    r'①-⑳'  # 丸付き数字 ①②③...
    r'⑴-⒛'
    r']'
)
PRINT_LOG_CALL = re.compile(
    r'^\s*(?:print|logging\.\w+)\s*\(', re.MULTILINE
)

# ==============================
# Rule 5: reconfigure未適用検出
# ==============================
RECONFIGURE_PATTERN = re.compile(r'sys\.stdout\.reconfigure|sys\.stderr\.reconfigure')
HAS_PRINT_OR_STDOUT = re.compile(r'\bprint\s*\(|sys\.stdout')

# ==============================
# チェック実行
# ==============================
for py_file in ROOT.rglob("*.py"):
    # スキップ
    if any(skip in py_file.parts for skip in SKIP_DIRS):
        continue
    if py_file.name == "check_utf8_mandate.py":
        continue

    try:
        text = py_file.read_text(encoding="utf-8", errors="replace")
    except Exception:
        continue

    lines = text.splitlines()
    rel = py_file.relative_to(ROOT)

    for i, line in enumerate(lines, 1):
        # Rule 1: open()にencoding=なし
        if "open(" in line and "encoding" not in line and "#" not in line.split("open(")[0]:
            if any(kw in line for kw in [".csv", ".json", ".txt", ".md", ".log"]):
                VIOLATIONS.append(
                    f"[Rule1] {rel}:{i} -> encoding未指定: {line.strip()[:60]}"
                )

        # Rule 2: Shift-JIS系エンコーディング
        if re.search(r'encoding\s*=\s*["\'](?:cp932|shift.jis|shift_jis)["\']', line, re.IGNORECASE):
            VIOLATIONS.append(
                f"[Rule2] {rel}:{i} -> Shift-JIS検出: {line.strip()[:60]}"
            )

        # Rule 4: print/logging内の非ASCII装飾記号
        if re.match(r'^\s*(?:print|logging\.\w+)\s*\(', line):
            if NON_ASCII_DECORATORS.search(line):
                VIOLATIONS.append(
                    f"[Rule4] {rel}:{i} -> print/logging内に非ASCII装飾記号: {line.strip()[:60]}"
                )

    # Rule 5: CLI実行系スクリプトのreconfigure未適用
    # 対象: CLI_DIRS配下 かつ デーモン系でない かつ print/stdout出力あり
    top_dir = rel.parts[0] if rel.parts else ""
    if top_dir in CLI_DIRS:
        stem = py_file.stem
        if stem not in DAEMON_PATTERNS and not stem.startswith("__"):
            if HAS_PRINT_OR_STDOUT.search(text) and not RECONFIGURE_PATTERN.search(text):
                VIOLATIONS.append(
                    f"[Rule5] {rel} -> sys.stdout.reconfigure未適用 (CLI実行系)"
                )

# ==============================
# PowerShellチェック
# ==============================
for ps_file in ROOT.rglob("*.ps1"):
    if any(skip in ps_file.parts for skip in SKIP_DIRS):
        continue
    try:
        text = ps_file.read_text(encoding="utf-8", errors="replace")
    except Exception:
        continue

    lines = text.splitlines()
    rel = ps_file.relative_to(ROOT)
    for i, line in enumerate(lines, 1):
        if "Invoke-WebRequest" in line and "-Body" in line:
            VIOLATIONS.append(
                f"[Rule3] {rel}:{i} -> Invoke-WebRequest+Body検出(UTF-8違反リスク): {line.strip()[:60]}"
            )

# ==============================
# 結果出力
# ==============================
if VIOLATIONS:
    print(f"\n[WARN] UTF-8 mandate violations: {len(VIOLATIONS)}\n")
    for v in VIOLATIONS:
        print(f"  [NG] {v}")
    print("\n-> UTF8_MANDATE.md を参照して修正してください")
    sys.exit(1)
else:
    print("[OK] UTF-8 mandate: no violations. MoCKA is clean.")
    sys.exit(0)
