"""
raw_processor.py
MoCKA No-Token Architecture
役割: RAWフォルダのECOL/ECAPファイルを一括処理
      文字化け修正(cp932) -> キーワード分類 -> lever_essence.json更新
API通信: 一切なし (0円)
E20260418_009
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime

# ============================================================
# 設定
# ============================================================
RAW_DIR      = Path(r"C:\Users\sirok\MoCKA\data\storage\infield\RAW")
ARCHIVE_DIR  = Path(r"C:\Users\sirok\MoCKA\data\storage\infield\ARCHIVED")
ESSENCE_PATH = Path(r"C:\Users\sirok\planningcaliber\workshop\needle_eye_project\experiments\lever_essence.json")
RESULT_LOG   = Path(r"C:\Users\sirok\MoCKA\data\raw_process_result.json")

# ============================================================
# キーワード分類ルール (APIゼロ・ルールベース)
# ============================================================
INCIDENT_KEYWORDS = [
    "エラー", "error", "失敗", "バグ", "bug", "障害", "問題", "異常",
    "クラッシュ", "crash", "例外", "exception", "修正", "fix",
    "枯渇", "停止", "中断", "不具合", "警告", "warning", "タイムアウト",
    "timeout", "拒否", "rejected", "violated", "violation"
]

PHILOSOPHY_KEYWORDS = [
    "哲学", "原則", "方針", "思想", "理念", "設計思想", "コンセプト",
    "AIを信じるな", "文明", "制度", "縛れ", "証明", "記録", "継承",
    "自由を許し", "失敗は資産", "principle", "philosophy", "vision",
    "mission", "governance", "trust", "constitution"
]

OPERATION_KEYWORDS = [
    "手順", "実行", "インストール", "コマンド", "スクリプト", "実装",
    "デプロイ", "設定", "configure", "setup", "install", "run",
    "python", "powershell", "bash", "git", "commit", "push",
    "起動", "停止", "再起動", "パイプライン", "watchdog", "bat"
]


def fix_encoding(raw_bytes: bytes) -> str:
    """
    文字化けテキストを修正する。
    BOM除去 -> UTF-8 -> cp932(Shift-JIS) -> latin-1 の順で試行。
    """
    # BOM除去
    if raw_bytes.startswith(b'\xef\xbb\xbf'):
        raw_bytes = raw_bytes[3:]

    for enc in ['utf-8', 'cp932', 'shift-jis', 'latin-1']:
        try:
            return raw_bytes.decode(enc)
        except Exception:
            continue
    # 最終手段: エラーを無視してデコード
    return raw_bytes.decode('utf-8', errors='replace')


def classify_text(text: str) -> dict:
    """
    テキストをキーワードマッチでINCIDENT/PHILOSOPHY/OPERATIONに分類。
    各カテゴリのスコアを計算し、最高スコアのカテゴリに分類。
    """
    text_lower = text.lower()
    scores = {
        "INCIDENT":   sum(1 for kw in INCIDENT_KEYWORDS   if kw.lower() in text_lower),
        "PHILOSOPHY": sum(1 for kw in PHILOSOPHY_KEYWORDS if kw.lower() in text_lower),
        "OPERATION":  sum(1 for kw in OPERATION_KEYWORDS  if kw.lower() in text_lower),
    }

    # 最高スコアのカテゴリを選択
    best = max(scores, key=lambda k: scores[k])
    if scores[best] == 0:
        best = None  # 分類不能

    return {"scores": scores, "category": best}


def extract_summary(text: str, max_len: int = 200) -> str:
    """
    テキストから要約を抽出する（先頭の意味ある行を使用）。
    """
    # [user] / [assistant] タグを除去
    cleaned = re.sub(r'\[(user|assistant|system)\]\s*', '', text)
    # 文字化け文字を除去（ascii + 日本語のみ残す）
    cleaned = re.sub(r'[^\x20-\x7E\u3000-\u9FFF\uFF00-\uFFEF\u30A0-\u30FF\u3040-\u309F]', ' ', cleaned)
    # 連続スペースを圧縮
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    # 先頭から意味ある部分を抽出
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len] + "..."
    return cleaned


def process_file(json_path: Path) -> dict:
    """
    1ファイルを処理する。
    戻り値: {event_id, category, summary, scores, status}
    """
    raw = json_path.read_bytes()
    text_decoded = fix_encoding(raw)

    try:
        data = json.loads(text_decoded)
    except json.JSONDecodeError:
        return {"file": json_path.name, "status": "JSON_ERROR", "category": None}

    text = data.get("text", "")
    event_id = data.get("event_id", json_path.stem)
    source   = data.get("source", "unknown")

    if not text or len(text) < 10:
        return {"file": json_path.name, "event_id": event_id, "status": "EMPTY", "category": None}

    result = classify_text(text)
    summary = extract_summary(text)

    return {
        "file":     json_path.name,
        "event_id": event_id,
        "source":   source,
        "status":   "OK",
        "category": result["category"],
        "scores":   result["scores"],
        "summary":  summary,
    }


def update_essence(categorized: list, essence_path: Path):
    """
    分類結果をlever_essence.jsonに反映する。
    各カテゴリの最も代表的なサマリを選択して上書き。
    """
    if essence_path.exists():
        try:
            existing = json.loads(essence_path.read_text(encoding='utf-8'))
        except Exception:
            existing = {}
    else:
        existing = {}

    # カテゴリ別に収集
    by_cat = {"INCIDENT": [], "PHILOSOPHY": [], "OPERATION": []}
    for item in categorized:
        cat = item.get("category")
        if cat in by_cat and item.get("summary"):
            by_cat[cat].append(item["summary"])

    timestamp = datetime.now().isoformat()
    updated = False

    for cat, summaries in by_cat.items():
        if not summaries:
            continue
        # 複数ある場合は最初の3件を結合
        combined = " / ".join(summaries[:3])
        if existing.get(cat) != combined:
            existing[cat] = combined
            existing[f"{cat}_updated"] = timestamp
            existing[f"{cat}_source_count"] = len(summaries)
            updated = True
            print(f"[ESSENCE] 更新 [{cat}] {len(summaries)}件 -> {combined[:60]}...")

    if updated:
        essence_path.parent.mkdir(parents=True, exist_ok=True)
        essence_path.write_text(
            json.dumps(existing, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        print(f"[ESSENCE] lever_essence.json 更新完了")
    else:
        print(f"[ESSENCE] 変更なし")

    return updated


def main():
    print(f"[RAW_PROCESSOR] 開始 — {RAW_DIR}")
    print(f"[RAW_PROCESSOR] API通信: ゼロ / ルールベース分類")

    files = sorted(RAW_DIR.glob("*.json"))
    print(f"[RAW_PROCESSOR] 対象: {len(files)}件\n")

    results = []
    stats = {"OK": 0, "EMPTY": 0, "JSON_ERROR": 0, "UNCLASSIFIED": 0}

    for i, f in enumerate(files, 1):
        result = process_file(f)
        results.append(result)

        status = result.get("status", "?")
        cat    = result.get("category") or "未分類"
        scores = result.get("scores", {})

        if status == "OK":
            if result["category"]:
                stats["OK"] += 1
            else:
                stats["UNCLASSIFIED"] += 1
                cat = "未分類"
        else:
            stats[status] = stats.get(status, 0) + 1

        print(f"[{i:3d}/{len(files)}] {f.name[:50]:50s} -> {cat:12s} {scores}")

    print(f"\n[RAW_PROCESSOR] 処理完了")
    print(f"  分類成功:   {stats['OK']}件")
    print(f"  未分類:     {stats['UNCLASSIFIED']}件")
    print(f"  空ファイル: {stats.get('EMPTY', 0)}件")
    print(f"  JSONエラー: {stats.get('JSON_ERROR', 0)}件")

    # essence更新
    classified = [r for r in results if r.get("category")]
    print(f"\n[RAW_PROCESSOR] essence更新対象: {len(classified)}件")
    update_essence(classified, ESSENCE_PATH)

    # 結果ログ保存
    RESULT_LOG.parent.mkdir(parents=True, exist_ok=True)
    RESULT_LOG.write_text(
        json.dumps({
            "processed_at": datetime.now().isoformat(),
            "total": len(files),
            "stats": stats,
            "results": results
        }, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    print(f"\n[RAW_PROCESSOR] 結果ログ -> {RESULT_LOG}")


if __name__ == "__main__":
    main()
