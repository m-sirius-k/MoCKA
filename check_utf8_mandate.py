#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MoCKA UTF-8 鉄の掟 違反チェッカー
起動時に自動実行 → 違反があれば警告
"""
import os, sys, re
from pathlib import Path

ROOT = Path(r"C:\Users\sirok\MoCKA")
VIOLATIONS = []

# チェック対象外
SKIP_DIRS = {"__pycache__", ".git", "node_modules", "venv", ".venv"}

# ==============================
# Rule 1: open()にencoding指定なし
# ==============================
OPEN_NO_ENC = re.compile(r'open\s*\([^)]+\)(?![^)]*encoding)')
OPEN_WRONG  = re.compile(r'encoding\s*=\s*["\'](?!utf-8|utf-8-sig)[^"\']+["\']')

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
    for i, line in enumerate(lines, 1):
        # open()にencoding=なし（ファイル操作のみ）
        if "open(" in line and "encoding" not in line and "#" not in line.split("open(")[0]:
            if any(kw in line for kw in [".csv", ".json", ".txt", ".md", ".log"]):
                VIOLATIONS.append(f"[Rule1] {py_file.relative_to(ROOT)}:{i} → encoding未指定: {line.strip()[:60]}")

        # Shift-JIS系エンコーディング
        if re.search(r'encoding\s*=\s*["\'](?:cp932|shift.jis|shift_jis)["\']', line, re.IGNORECASE):
            VIOLATIONS.append(f"[Rule2] {py_file.relative_to(ROOT)}:{i} → Shift-JIS検出: {line.strip()[:60]}")

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
    for i, line in enumerate(lines, 1):
        # Invoke-WebRequestでJSON送信
        if "Invoke-WebRequest" in line and "-Body" in line:
            VIOLATIONS.append(f"[Rule3] {ps_file.relative_to(ROOT)}:{i} → Invoke-WebRequest+Body検出（UTF-8違反リスク）: {line.strip()[:60]}")

# ==============================
# 結果出力
# ==============================
if VIOLATIONS:
    print(f"\n⚠️  UTF-8鉄の掟 違反検出: {len(VIOLATIONS)}件\n")
    for v in VIOLATIONS:
        print(f"  ❌ {v}")
    print("\n→ UTF8_MANDATE.md を参照して修正してください")
    sys.exit(1)
else:
    print("✅ UTF-8鉄の掟 違反なし。MoCKAは清潔です。")
    sys.exit(0)