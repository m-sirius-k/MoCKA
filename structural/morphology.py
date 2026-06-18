# -*- coding: utf-8 -*-
import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
"""
structural/morphology.py — 事象→構造タグ変換層（TODO_211）
Structural Intelligence パイプライン第1段。
テキスト or TICイベントを入力し、pattern_db.json の構造タグリストを返す。
既存の interface/morphology_engine.py の形態素解析を可能なら流用する。
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT         = Path(__file__).parent.parent
PATTERN_DB   = Path(__file__).parent / "pattern_db.json"
MORPHO_ENGINE = ROOT / "interface" / "morphology_engine.py"

# ─── pattern_db 読み込み ─────────────────────────────────────────────────────

def _load_pattern_db() -> dict:
    if PATTERN_DB.exists():
        return json.loads(PATTERN_DB.read_text(encoding="utf-8"))
    return {}

_PATTERN_DB = _load_pattern_db()

# ─── キーワードマッチによる構造タグ付与 ─────────────────────────────────────

def _keyword_match(text: str, pattern_db: dict) -> list[str]:
    """pattern_db のキーワードリストとテキストを照合して構造タグを返す"""
    text_lower = text.lower()
    matched = []
    for tag, entry in pattern_db.items():
        if tag.startswith("_"):
            continue
        keywords = entry.get("keywords", [])
        if any(kw.lower() in text_lower for kw in keywords):
            matched.append(tag)
    return matched

# ─── 形態素解析（Janome が使える場合のみ） ──────────────────────────────────

def _morpho_tokenize(text: str) -> list[str]:
    """Janome で形態素解析し、重要単語リストを返す。失敗時は空リスト。"""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("morphology_engine", MORPHO_ENGINE)
        me = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(me)
        tokens = me.tokenize(text)
        return [t["surface"] for t in tokens]
    except Exception:
        # Janome 未インストール or エンジンエラー → フォールバック
        return re.findall(r"[\w぀-鿿]{2,}", text)

# ─── メイン API ─────────────────────────────────────────────────────────────

def analyze(text: str, source_event_id: str = None) -> dict:
    """
    テキストを構造タグリストに変換する。

    Returns:
        {
          "event": str,
          "structures": [tag, ...],
          "tag_details": [{tag, category, risk_level, stability}, ...],
          "raw_text": str,
          "timestamp": str,
          "source_event_id": str | None,
        }
    """
    pdb = _PATTERN_DB

    # 1. キーワードマッチ
    keyword_tags = _keyword_match(text, pdb)

    # 2. 形態素解析トークンで追加マッチ
    tokens = _morpho_tokenize(text)
    token_text = " ".join(tokens)
    token_tags = _keyword_match(token_text, pdb) if token_text else []

    # 重複除去・結合
    all_tags = list(dict.fromkeys(keyword_tags + token_tags))

    # タグの詳細情報を付与
    tag_details = []
    for tag in all_tags:
        entry = pdb.get(tag, {})
        tag_details.append({
            "tag":        tag,
            "category":   entry.get("category", "unknown"),
            "risk_level": entry.get("risk_level", "unknown"),
            "stability":  entry.get("stability", "unknown"),
        })

    # イベント名（最初のキーワードから推定）
    event_name = _infer_event_name(text)

    return {
        "event":           event_name,
        "structures":      all_tags,
        "tag_details":     tag_details,
        "raw_text":        text,
        "timestamp":       datetime.now().isoformat(),
        "source_event_id": source_event_id,
    }


def _infer_event_name(text: str) -> str:
    """テキストから簡易的なイベント名を推定する（英数字スネークケース）"""
    # 先頭30文字をスネークケースに変換
    s = re.sub(r"[^\w]", "_", text[:40].lower())
    s = re.sub(r"_+", "_", s).strip("_")
    return s[:30] or "unknown_event"


# ─── CLI ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample_texts = [
        "Claude DOM変更でRelayが壊れた",
        "MCP普及で公式インターフェース移行が進んでいる",
        "急成長後に大障害が発生した",
        "health_check.pyで無音崩壊を検知する仕組みを作った",
    ]
    for t in sample_texts:
        result = analyze(t)
        print(f"\n入力: {t}")
        print(f"  構造タグ: {result['structures']}")
