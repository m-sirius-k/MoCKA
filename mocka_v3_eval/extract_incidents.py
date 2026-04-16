"""
extract_incidents.py
REDUCING + RE_REDUCED フォルダの全JSONを走査し
インシデント候補をキーワードマッチで抽出
→ incidents_candidates.json に出力
"""
import json
import csv
import hashlib
from pathlib import Path
from datetime import datetime, timezone

# ── パス ──────────────────────────────────────────────────
ROOT        = Path(r"C:\Users\sirok\MoCKA")
REDUCING    = ROOT / "data" / "storage" / "infield" / "REDUCING"
RE_REDUCED  = ROOT / "data" / "storage" / "infield" / "RE_REDUCED"
OUTPUT      = ROOT / "data" / "experiments" / "incidents_candidates.json"
EVENTS_CSV  = ROOT / "data" / "events.csv"

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

# ── インシデントキーワード ─────────────────────────────────
INCIDENT_KEYWORDS = [
    # 問題・障害系
    "error", "fail", "broke", "crash", "bug", "issue", "problem",
    "not work", "doesn't work", "couldn't", "unable", "exception",
    "traceback", "syntax error", "permission denied", "timeout",
    # 再発系
    "again", "repeated", "recur", "same issue", "same problem",
    "still", "yet again", "once more", "keep happening",
    # AI違反系
    "unauthorized", "overwrite", "ignore", "violat", "instruction_ignore",
    "without permission", "unexpected",
    # セキュリティ系
    "token", "secret", "api key", "credential", "leak", "commit",
    "accidentally", "exposed",
    # 日本語
    "エラー", "失敗", "壊れ", "動かない", "おかしい", "バグ",
    "また", "再び", "繰り返し", "同じ問題", "同じエラー",
    "無断", "上書き", "漏洩", "誤って", "問題", "不具合",
    "できない", "止まった", "止まる", "落ちた",
]

# ── 抽出関数 ──────────────────────────────────────────────
def score_text(text: str) -> tuple[int, list[str]]:
    """テキストにインシデントキーワードが何個含まれるか"""
    text_lower = text.lower()
    matched = [kw for kw in INCIDENT_KEYWORDS if kw.lower() in text_lower]
    return len(matched), matched

def extract_from_file(fpath: Path, folder: str) -> dict | None:
    try:
        data = json.loads(fpath.read_text("utf-8"))
    except Exception:
        return None

    # フォルダによってフィールド名が違う
    if folder == "REDUCING":
        text = data.get("extraction", "")
    else:  # RE_REDUCED
        text = data.get("core_insight", "") + " " + data.get("full_summary", "")

    if not text.strip():
        return None

    score, matched = score_text(text)
    if score == 0:
        return None

    return {
        "file"       : fpath.name,
        "folder"     : folder,
        "source"     : data.get("source", "unknown"),
        "timestamp"  : data.get("timestamp", ""),
        "restore_rate": data.get("restore_rate", 0),
        "score"      : score,
        "matched_keywords": matched[:5],
        "excerpt"    : text[:300],
        "event_id"   : data.get("event_id", ""),
    }

# ── メイン ────────────────────────────────────────────────
def main():
    candidates = []

    for folder, path in [("REDUCING", REDUCING), ("RE_REDUCED", RE_REDUCED)]:
        files = sorted(path.glob("*.json"))
        print(f"[{folder}] {len(files)} files")
        for f in files:
            result = extract_from_file(f, folder)
            if result:
                candidates.append(result)

    # スコア降順でソート
    candidates.sort(key=lambda x: x["score"], reverse=True)

    print(f"\n✓ インシデント候補: {len(candidates)} 件 / 全体から抽出")
    print(f"  スコア分布:")
    for threshold in [5, 3, 2, 1]:
        count = sum(1 for c in candidates if c["score"] >= threshold)
        print(f"  score >= {threshold}: {count} 件")

    # 上位20件をプレビュー
    print(f"\n=== 上位10件プレビュー ===")
    for c in candidates[:10]:
        print(f"[{c['score']}pts] {c['source']} | {c['file'][:30]}")
        print(f"  keywords: {c['matched_keywords']}")
        print(f"  excerpt : {c['excerpt'][:100]}")
        print()

    # JSON出力
    output = {
        "extracted_at" : datetime.now(timezone.utc).isoformat(),
        "total_files_scanned": sum(len(list(p.glob("*.json"))) for p in [REDUCING, RE_REDUCED]),
        "incident_candidates": len(candidates),
        "candidates": candidates
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ 保存 → {OUTPUT}")

if __name__ == "__main__":
    main()
