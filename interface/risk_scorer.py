"""
risk_scorer.py  -- TIC Risk Score Calculator
dependency_map.json の各エントリに Risk Score (0-100) を計算して付与する。

スコア計算式（きむら博士設計）:
  change_frequency:  critical=40, high=30, medium=20, low=10
  substitutability:  none=30, hard=20, easy=5
  blast_radius_score: global=30, command_center=20, それ以外=len()*5 (max 20)
  risk_score = sum (上限100)
"""

import json
import datetime
import sys
import io
from pathlib import Path

# Windows cp932 環境でも確実に出力できるよう utf-8 強制
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

MAP_PATH = Path("C:/Users/sirok/MoCKA/data/tic/dependency_map.json")
MCP_URL  = "http://localhost:5002/agent/mocka_write_event"

FREQ_SCORE  = {"critical": 40, "high": 30, "medium": 20, "low": 10}
SUBST_SCORE = {"none": 30, "hard": 20, "easy": 5}

RANK_LABELS = {
    (70, 101): ("CRITICAL", "\033[91m"),
    (50,  70): ("WARNING",  "\033[93m"),
    (30,  50): ("CAUTION",  "\033[33m"),
    ( 0,  30): ("STABLE",   "\033[92m"),
}
RESET = "\033[0m"


def blast_score(blast_radius: list) -> int:
    joined = " ".join(blast_radius).lower()
    if "global" in joined:
        return 30
    if "command_center" in joined:
        return 20
    return min(len(blast_radius) * 5, 20)


def calc_score(dep: dict) -> int:
    freq = dep.get("change_frequency", "low")
    s = (
        FREQ_SCORE.get(freq, 10)
        + SUBST_SCORE.get(dep.get("substitutability", "easy"), 5)
        + blast_score(dep.get("blast_radius", []))
    )
    score = min(max(s, 0), 100)
    # critical 扱いの場合は最低 80 を保証（Human Gate 判断による下限）
    if freq == "critical":
        score = max(score, 80)
    return score


def rank(score: int) -> tuple:
    for (lo, hi), (label, color) in RANK_LABELS.items():
        if lo <= score < hi:
            return label, color
    return "STABLE", "\033[92m"


def write_event(title: str, description: str, tags: str = "tic,risk_score"):
    try:
        import urllib.request
        payload = json.dumps({
            "title": title,
            "description": description,
            "tags": tags,
            "why_purpose": "TICリスクスコア計算",
            "how_trigger": "risk_scorer.py",
        }).encode("utf-8")
        req = urllib.request.Request(
            MCP_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        pass  # MoCKAサーバー未起動でも継続


def run():
    if not MAP_PATH.exists():
        print(f"[ERROR] {MAP_PATH} not found")
        sys.exit(1)

    data = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    deps = data["dependencies"]

    now = datetime.datetime.now().isoformat()
    results = []
    for dep in deps:
        score = calc_score(dep)
        dep["risk_score"]    = score
        dep["last_verified"] = now
        label, color         = rank(score)
        results.append((dep["component"], score, label, color))

    # in-place 更新
    data["meta"]["updated_by"] = f"risk_scorer.py @ {now}"
    MAP_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # ── コンソール出力 ──
    results.sort(key=lambda x: x[1], reverse=True)
    width = max(len(r[0]) for r in results)

    print()
    print("=" * 50)
    print(f"  Today's Technical Risk Summary  {datetime.date.today()}")
    print("=" * 50)
    for comp, score, label, color in results:
        bar = "#" * (score // 5)
        print(f"  {comp:<{width}}  {color}{score:>3}  [{label:<8}]{RESET}  {bar}")
    print("=" * 50)
    critical = [r for r in results if r[2] == "CRITICAL"]
    warning  = [r for r in results if r[2] == "WARNING"]
    print(f"  CRITICAL: {len(critical)}件  WARNING: {len(warning)}件")
    print("=" * 50)
    print()

    # MoCKA 記録
    summary = ", ".join(f"{c}:{s}" for c, s, _, _ in results[:3])
    write_event(
        "RISK_SCORE_UPDATED: TICリスクスコア計算完了",
        f"全{len(results)}件更新。上位3件: {summary}",
        "tic,risk_score",
    )

    return data


if __name__ == "__main__":
    run()
