"""
risk_interpreter.py -- TIC Risk Interpreter (Phase 1)

risk_scorer.py が計算した dependency_map.json を読み込み、各コンポーネントの
スコアに対して決定論的な "why"（根拠テキスト）を付与する。

- AI呼び出しなし。change_frequency / substitutability / blast_radius から
  固定のフレーズを組み合わせて生成する。
- override_metadata.json を読み、expires を過ぎていれば override を無効化し
  計算値（risk_score再計算）を採用する。
- risk_scorer.py のコア計算ロジック（calc_score）は変更しない。
"""

import json
import datetime
import sys
import io
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from risk_scorer import calc_score, rank, FREQ_SCORE, SUBST_SCORE, blast_score, RESET

MAP_PATH      = Path("C:/Users/sirok/MoCKA/data/tic/dependency_map.json")
OVERRIDE_PATH = Path("C:/Users/sirok/MoCKA/data/tic/override_metadata.json")

FREQ_PHRASES = {
    "critical": "外部仕様変更が極めて高頻度",
    "high":     "変更頻度が高い",
    "medium":   "変更頻度は中程度",
    "low":      "変更頻度は低い",
}

SUBST_PHRASES = {
    "none": "代替手段なし",
    "hard": "代替は困難",
    "easy": "代替は容易",
}


def blast_phrase(blast_radius: list) -> str:
    joined = " ".join(blast_radius).lower()
    if "global" in joined:
        return "全システム影響範囲"
    if "command_center" in joined:
        return "中枢機能に影響"
    return f"{len(blast_radius)}コンポーネントに影響"


def generate_why(dep: dict) -> str:
    freq  = dep.get("change_frequency", "low")
    subst = dep.get("substitutability", "easy")
    blast = dep.get("blast_radius", [])
    parts = [
        FREQ_PHRASES.get(freq, "変更頻度は低い"),
        SUBST_PHRASES.get(subst, "代替は容易"),
        blast_phrase(blast),
    ]
    return "・".join(parts)


def load_overrides() -> dict:
    if OVERRIDE_PATH.exists():
        return json.loads(OVERRIDE_PATH.read_text(encoding="utf-8"))
    return {}


def interpret(dep: dict, overrides: dict, today: datetime.date) -> dict:
    comp = dep["component"]
    why  = generate_why(dep)

    override_entry = overrides.get(comp)
    override_active = False
    override_reason = None
    expires = None

    calc = calc_score(dep)

    if override_entry:
        expires_str = override_entry.get("expires")
        expires = expires_str
        expired = False
        if expires_str:
            try:
                expired = today > datetime.date.fromisoformat(expires_str)
            except ValueError:
                expired = False

        if not expired:
            override_active = True
            override_reason = override_entry.get("reason")
            score = override_entry.get("override_value", calc)
        else:
            score = calc
    else:
        score = calc

    label, color = rank(score)

    return {
        "component":       comp,
        "score":           score,
        "rank":            label,
        "why":             why,
        "override":        override_active,
        "override_reason": override_reason,
        "expires":         expires,
        "_color":          color,
    }


def run():
    if not MAP_PATH.exists():
        print(f"[ERROR] {MAP_PATH} not found")
        sys.exit(1)

    data      = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    overrides = load_overrides()
    today     = datetime.date.today()

    results = [interpret(dep, overrides, today) for dep in data["dependencies"]]
    results.sort(key=lambda r: r["score"], reverse=True)

    width = max(len(r["component"]) for r in results)

    print()
    print("=" * 70)
    print(f"  Today's Technical Risk Summary  {today}")
    print("=" * 70)
    for r in results:
        print(
            f"  {r['component']:<{width}}  {r['_color']}{r['score']:>3}  "
            f"[{r['rank']:<8}]{RESET}  {r['why']}"
        )
    print("=" * 70)
    print()

    return results


if __name__ == "__main__":
    run()
