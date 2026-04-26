"""
pattern_registry_seed.py
MoCKA Pattern Registry 初期シード投入スクリプト

機能:
  1. pattern_registry.csv の手動シードをロード
  2. events.csv から過去のINCIDENT/DANGERイベントを読み込みN-gramを自動抽出
  3. success_patterns.json（ヒント！/グレイト！データ）があれば成功パターンも抽出
  4. 結合してpattern_registry.csvを書き出す

実行:
  python pattern_registry_seed.py
  python pattern_registry_seed.py --from-events  # events.csvから自動抽出も実施

配置先: C:/Users/sirok/MoCKA/interface/pattern_registry_seed.py
"""

import argparse
import csv
import json
import os
import re
from datetime import datetime
from pathlib import Path

# pattern_engine_v2 をインポート（同じディレクトリにある前提）
import sys
sys.path.insert(0, str(Path(__file__).parent))

try:
    from pattern_engine_v2 import PatternEngine, PatternRegistry, tokenize_mecab, _fallback_tokenize, extract_ngrams, REGISTRY_PATH, EVENTS_CSV, SUCCESS_PATTERNS_PATH
except ImportError:
    print("[ERROR] pattern_engine_v2.py が見つかりません。同じディレクトリに配置してください。")
    sys.exit(1)

BASE_DIR = Path(os.environ.get("MOCKA_ROOT", "C:/Users/sirok/MoCKA"))
SEED_CSV  = Path(__file__).parent / "pattern_registry_seed_data.csv"

# ─── イベント種別→outcome マッピング ──────────────────────────────────────────
OUTCOME_MAP = {
    # 失敗・危険系
    "INCIDENT":         "DANGER",
    "ERROR":            "DANGER",
    "CRITICAL":         "DANGER",
    "DEPENDENCY_BREAK": "DANGER",
    "ai_violation":     "DANGER",
    "WARNING":          "DANGER",
    # 成功系
    "save":             "SUCCESS",
    "collaboration":    "SUCCESS",
    "share":            "SUCCESS",
    "record":           "SUCCESS",
    "generation":       "SUCCESS",
    "essence_update":   "SUCCESS",
    "ingest":           "SUCCESS",
    # 処理系（テキストが豊富なもの）
    "process":          "SUCCESS",
    "collect":          "SUCCESS",
    "broadcast":        "SUCCESS",
    "claude_mcp":       "SUCCESS",
    "storage":          "SUCCESS",
    # スキップ（空・パイプライン段階名）
    "":                 None,
    "RAW":              None,
    "RE_REDUCED":       None,
    "REDUCING":         None,
    "OPERATION":        None,
    "response":         None,
    "playwright_capture": None,
}


def events_to_patterns(events_path: Path, engine: PatternEngine, limit: int = 200):
    """events.csv のwhat/detailフィールドからN-gramを抽出してDBに追加する。"""
    if not events_path.exists():
        print(f"[SKIP] {events_path} が存在しません")
        return 0

    added = 0
    with open(events_path, encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # 直近limit件を対象
    rows = rows[-limit:]

    # MeCab疎通を1回だけ確認（タイムアウト×4991行を防ぐ）
    mecab_ok = False
    try:
        import socket as _s
        with _s.create_connection(("127.0.0.1", 5003), timeout=1.0):
            mecab_ok = True
    except Exception:
        pass
    tokenize_fn = tokenize_mecab if mecab_ok else _fallback_tokenize
    print(f"  トークナイザー: {'MeCab WSL:5003' if mecab_ok else 'fallback (MeCab未接続)'}")

    for row in rows:
        what_type = row.get("what_type", "")
        detail    = row.get("detail", "") or row.get("why_purpose", "")
        if not detail or len(detail) < 5:
            continue

        outcome = OUTCOME_MAP.get(what_type)
        if outcome is None:
            continue  # スキップ対象

        tokens = tokenize_fn(detail)

        ngrams = extract_ngrams(tokens, n=3)
        for ng in ngrams:
            engine.registry.update_pattern(ng, outcome, source="events_seed")
            added += 1

    print(f"[events_seed] {added} パターンをevents.csvから抽出・更新")
    return added


def success_patterns_to_registry(sp_path: Path, engine: PatternEngine):
    """success_patterns.json からSUCCESSパターンを追加する。"""
    if not sp_path.exists():
        print(f"[SKIP] {sp_path} が存在しません（TODO_076実装後に再実行）")
        return 0

    with open(sp_path, encoding="utf-8") as f:
        data = json.load(f)

    added = 0
    for item in data.get("patterns", []):
        text    = item.get("text", "")
        outcome = item.get("outcome", "SUCCESS")
        if not text:
            continue
        try:
            tokens = tokenize_mecab(text)
        except Exception:
            tokens = _fallback_tokenize(text)
        ngrams = extract_ngrams(tokens, n=3)
        for ng in ngrams:
            engine.registry.update_pattern(ng, outcome, source="success_seed")
            added += 1

    print(f"[success_seed] {added} パターンをsuccess_patterns.jsonから抽出・更新")
    return added


def print_stats(registry: PatternRegistry):
    total = len(registry.records)
    danger  = sum(1 for r in registry.records.values() if r["outcome"] == "DANGER")
    success = sum(1 for r in registry.records.values() if r["outcome"] == "SUCCESS")
    tier1   = sum(1 for r in registry.records.values() if r["tier"] == 1)
    print(f"\n{'='*50}")
    print(f"  pattern_registry.csv 統計")
    print(f"{'='*50}")
    print(f"  総パターン数 : {total}")
    print(f"  DANGER       : {danger}")
    print(f"  SUCCESS      : {success}")
    print(f"  NEUTRAL/DRIFT: {total - danger - success}")
    print(f"  Tier 1       : {tier1}")
    print(f"  保存先       : {REGISTRY_PATH}")
    print(f"{'='*50}\n")


def main():
    parser = argparse.ArgumentParser(description="MoCKA Pattern Registry シード投入")
    parser.add_argument("--from-events",    action="store_true", help="events.csvからN-gramを自動抽出")
    parser.add_argument("--from-success",   action="store_true", help="success_patterns.jsonから抽出")
    parser.add_argument("--events-path",    default=str(EVENTS_CSV))
    parser.add_argument("--success-path",   default=str(SUCCESS_PATTERNS_PATH))
    parser.add_argument("--limit",          type=int, default=200, help="events.csvの最大読み込み行数")
    parser.add_argument("--dry-run",        action="store_true", help="保存せずに統計のみ表示")
    args = parser.parse_args()

    print(f"[{datetime.now().isoformat()}] Pattern Registry Seed 開始")
    print(f"  Registry path: {REGISTRY_PATH}")

    engine = PatternEngine()
    initial_count = len(engine.registry.records)
    print(f"  初期パターン数: {initial_count}")

    if args.from_events:
        events_to_patterns(Path(args.events_path), engine, limit=args.limit)

    if args.from_success:
        success_patterns_to_registry(Path(args.success_path), engine)

    print_stats(engine.registry)

    if not args.dry_run:
        engine.registry.save()
        print(f"[完了] {REGISTRY_PATH} に保存しました")
    else:
        print("[dry-run] 保存はスキップしました")


if __name__ == "__main__":
    main()
