#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MoCKA Phase 2 — app.py CSV→SQLite切替パッチ

対象3関数:
  next_event_id() → db_helper.get_next_event_id()
  append_event()  → db_helper.write_event()
  load_history()  → db_helper.read_events()

実行:
  python app_patch_phase2.py --dry-run  # 変更箇所確認のみ
  python app_patch_phase2.py            # 本番パッチ適用
  python app_patch_phase2.py --restore  # バックアップから復元
"""

import re
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime

APP_PATH    = Path(r"C:\Users\sirok\MoCKA\app.py")
BACKUP_PATH = Path(r"C:\Users\sirok\MoCKA\app.py.bak_phase2")

# ============================================================
# パッチ定義（old → new）
# ============================================================
PATCHES = [
    # ① importにdb_helperを追加（csv importの直後）
    {
        "desc": "db_helper import追加",
        "old": "import csv\n",
        "new": "import csv\nimport sys as _sys\n_sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent / 'interface'))\nimport db_helper\n",
    },

    # ② next_event_id() → db_helper委譲
    {
        "desc": "next_event_id() → db_helper委譲",
        "old": """def next_event_id():
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"E{today}_"
    ensure_events_csv()
    last_n = 0
    with open(EVENTS_CSV, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            ev = (r.get("event_id") or "").strip()
            if ev.startswith(prefix):
                parts = ev.split("_")
                if len(parts) == 2:
                    try:
                        n = int(parts[1])
                        if n > last_n:
                            last_n = n
                    except ValueError:
                        pass
    return f"{prefix}{last_n+1:03d}"
""",
        "new": """def next_event_id():
    return db_helper.get_next_event_id()
""",
    },

    # ③ append_event() → db_helper委譲（CSV書き込み部分のみ）
    {
        "desc": "append_event() CSV書き込み → db_helper委譲",
        "old": """    with open(EVENTS_CSV, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(row)
""",
        "new": """    db_helper.write_event(row)
""",
    },

    # ④ load_history() → db_helper委譲
    {
        "desc": "load_history() → db_helper委譲",
        "old": """def load_history(limit=None):
    ensure_events_csv()
    rows = []
    with open(EVENTS_CSV, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            clean = {k: (v if v is not None else "") for k, v in r.items()}
            rows.append(clean)
    if limit is not None:
        rows = rows[-int(limit):]""",
        "new": """def load_history(limit=None):
    rows = db_helper.read_events(limit=int(limit) if limit else None)
    # 既存コードとの互換性: 全フィールドを文字列に正規化
    rows = [{k: (v if v is not None else "") for k, v in r.items()} for r in rows]""",
    },
]


def apply_patches(dry_run: bool = False):
    print("=" * 60)
    print("MoCKA Phase 2: app.py CSV→SQLite切替パッチ")
    print(f"  対象: {APP_PATH}")
    print(f"  Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print("=" * 60)

    if not APP_PATH.exists():
        print(f"[ERROR] app.pyが見つかりません: {APP_PATH}")
        sys.exit(1)

    content = APP_PATH.read_text(encoding="utf-8")
    original = content

    results = []
    for patch in PATCHES:
        if patch["old"] in content:
            if not dry_run:
                content = content.replace(patch["old"], patch["new"], 1)
            results.append(("OK", patch["desc"]))
        else:
            results.append(("SKIP", patch["desc"]))

    print("\nパッチ適用結果:")
    for status, desc in results:
        mark = "✓" if status == "OK" else "△"
        print(f"  [{status}] {mark} {desc}")

    skipped = [d for s, d in results if s == "SKIP"]
    if skipped:
        print(f"\n[INFO] SKIPされたパッチ（既に適用済みか構造が変化）:")
        for d in skipped:
            print(f"  - {d}")

    if dry_run:
        print("\n[DRY RUN完了] 変更は適用されていません")
        return

    if content == original:
        print("\n[INFO] 変更なし（全パッチ適用済みの可能性）")
        return

    # バックアップ作成
    shutil.copy2(APP_PATH, BACKUP_PATH)
    print(f"\n[BACKUP] {BACKUP_PATH}")

    # 書き込み
    APP_PATH.write_text(content, encoding="utf-8")
    print(f"[OK] app.py更新完了")

    # 確認
    verify_patch()


def verify_patch():
    """パッチ適用後の確認"""
    print("\n" + "=" * 60)
    print("パッチ確認")
    print("=" * 60)
    content = APP_PATH.read_text(encoding="utf-8")

    checks = [
        ("import db_helper",            "db_helper import"),
        ("db_helper.get_next_event_id", "next_event_id委譲"),
        ("db_helper.write_event",       "append_event委譲"),
        ("db_helper.read_events",       "load_history委譲"),
    ]

    all_ok = True
    for keyword, desc in checks:
        found = keyword in content
        mark = "✓" if found else "✗"
        print(f"  [{mark}] {desc}")
        if not found:
            all_ok = False

    if all_ok:
        print("\n[OK] Phase 2パッチ PASSED ✓")
    else:
        print("\n[WARN] 一部パッチが未適用です")


def restore():
    """バックアップから復元"""
    if not BACKUP_PATH.exists():
        print(f"[ERROR] バックアップが見つかりません: {BACKUP_PATH}")
        sys.exit(1)
    shutil.copy2(BACKUP_PATH, APP_PATH)
    print(f"[OK] 復元完了: {BACKUP_PATH} → {APP_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run",  action="store_true")
    parser.add_argument("--verify",   action="store_true")
    parser.add_argument("--restore",  action="store_true")
    args = parser.parse_args()

    if args.restore:
        restore()
    elif args.verify:
        verify_patch()
    else:
        apply_patches(dry_run=args.dry_run)
