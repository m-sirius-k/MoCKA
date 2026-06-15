"""
trend_engine.py -- TIC Trend Engine (Phase5)

risk_history.jsonl（Phase2）から各コンポーネントの過去最大7日分のスコアを読み、
純粋Pythonの最小二乗法でslopeを計算し、trend_history.jsonlにappendする。

- 外部ライブラリ不使用（numpy/scipy禁止）
- 予測はしない。傾向の記録のみ
- 同日・同コンポーネントは重複記録しない（冪等性）
"""

import json
import datetime
import sys
import io
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HISTORY_PATH       = Path("C:/Users/sirok/MoCKA/data/tic/risk_history.jsonl")
TREND_HISTORY_PATH = Path("C:/Users/sirok/MoCKA/data/tic/trend_history.jsonl")

WINDOW_DAYS = 7


def _load_jsonl(path: Path) -> list:
    if not path.exists():
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    return out


def load_history() -> list:
    """date昇順のhistoryエントリを返す（同日重複は最後のものを優先）"""
    entries = _load_jsonl(HISTORY_PATH)
    by_date = {}
    for e in entries:
        by_date[e.get("date")] = e
    return [by_date[d] for d in sorted(by_date.keys())]


def get_score_series(component: str, history: list, window: int = WINDOW_DAYS) -> list:
    series = []
    for entry in history:
        score = entry.get("scores", {}).get(component)
        if score is not None:
            series.append(score)
    return series[-window:]


def least_squares_slope(scores: list) -> float:
    n = len(scores)
    if n < 2:
        return 0.0
    xs = list(range(n))
    sum_x  = sum(xs)
    sum_y  = sum(scores)
    sum_xy = sum(x * y for x, y in zip(xs, scores))
    sum_x2 = sum(x * x for x in xs)
    denom = n * sum_x2 - sum_x * sum_x
    if denom == 0:
        return 0.0
    return (n * sum_xy - sum_x * sum_y) / denom


def classify_trend(slope: float) -> str:
    if slope > 2.0:
        return "INCREASING"
    if slope < -2.0:
        return "IMPROVING"
    return "STABLE"


def calc_confidence(n: int) -> float:
    if n >= 7:
        return 0.90
    if n >= 4:
        return 0.75
    if n >= 2:
        return 0.60
    return 0.40


def run():
    history = load_history()
    if not history:
        print("[trend_engine] risk_history.jsonl が空。終了。")
        return []

    today_str  = datetime.date.today().isoformat()
    existing   = _load_jsonl(TREND_HISTORY_PATH)
    done_comps = {e["component"] for e in existing if e.get("date") == today_str}
    seq        = len(existing)

    components = sorted(history[-1].get("scores", {}).keys())

    new_entries = []
    for comp in components:
        if comp in done_comps:
            continue

        series = get_score_series(comp, history)
        slope  = least_squares_slope(series)
        trend  = classify_trend(slope)
        conf   = calc_confidence(len(series))

        seq += 1
        entry = {
            "trend_id":    f"TR_{seq:06d}",
            "component":   comp,
            "date":        today_str,
            "scores":      series,
            "trend":       trend,
            "slope":       round(slope, 1),
            "window_days": WINDOW_DAYS,
            "confidence":  conf,
        }
        new_entries.append(entry)

    if new_entries:
        TREND_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TREND_HISTORY_PATH, "a", encoding="utf-8") as f:
            for entry in new_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"[trend_engine] {len(new_entries)}件記録（本日合計: {len(done_comps) + len(new_entries)}件）")
    for entry in new_entries:
        sign = "+" if entry["slope"] >= 0 else ""
        print(
            f"  {entry['trend_id']}  {entry['component']:<20} "
            f"[{entry['trend']:<10}]  slope={sign}{entry['slope']}  "
            f"conf={entry['confidence']}  n={len(entry['scores'])}"
        )

    return new_entries


if __name__ == "__main__":
    run()
