"""
root_cause_engine.py -- TIC Root Cause Engine (Phase4)

dependency_events.jsonl（Phase2）の当日変化イベントを読み、
dependency_graph.jsonl（Phase3）を辿ってcause_chainを生成し、
決定論的なreasonテキストとともに root_cause.jsonl にappendする。

- AI呼び出しなし（テンプレートベース）
- 判断・予測はしない。記録のみ
- 同日・同コンポーネントは重複記録しない（冪等性）
"""

import json
import datetime
import sys
import io
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from graph_loader import load_edges, get_impacts

EVENTS_PATH     = Path("C:/Users/sirok/MoCKA/data/tic/dependency_events.jsonl")
ROOT_CAUSE_PATH = Path("C:/Users/sirok/MoCKA/data/tic/root_cause.jsonl")

MAX_HOPS = 3


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


def _load_events_today() -> list:
    today_str = datetime.date.today().isoformat()
    return [e for e in _load_jsonl(EVENTS_PATH) if e.get("date") == today_str]


def build_cause_chain(component: str, edges: list) -> tuple:
    """impactsエッジを辿ってcause_chainを生成（最大3ホップ）。
    戻り値: (chain: list[str], all_verified: bool)"""
    chain = [component]
    all_verified = True
    current = component

    for _ in range(MAX_HOPS):
        impact_edges = [
            e for e in edges
            if e["from"] == current and e["type"] == "impacts" and e["to"] not in chain
        ]
        if not impact_edges:
            break
        nxt = impact_edges[0]
        chain.append(nxt["to"])
        if not nxt.get("verified", False):
            all_verified = False
        current = nxt["to"]

    return chain, all_verified


def generate_reason(component: str, delta: int, target: str) -> str:
    if delta > 0:
        return f"{component}の外部依存が変化し、{target}へのリスクが上昇（+{delta}）"
    return f"{component}の状況が改善し、{target}へのリスクが低下（{delta}）"


def calc_confidence(chain: list, all_verified: bool) -> float:
    confidence = 0.90 if all_verified else 0.70
    if len(chain) >= 4:
        confidence -= 0.05
    return round(confidence, 2)


def run():
    events_today = _load_events_today()
    if not events_today:
        print("[root_cause_engine] dependency_events.jsonl に本日の変化なし。終了。")
        return []

    existing   = _load_jsonl(ROOT_CAUSE_PATH)
    today_str  = datetime.date.today().isoformat()
    done_comps = {e["component"] for e in existing if e.get("date") == today_str}
    seq        = len(existing)

    edges = load_edges()
    new_entries = []

    for ev in events_today:
        comp = ev["component"]
        if comp in done_comps:
            continue

        chain, all_verified = build_cause_chain(comp, edges)
        impacts = get_impacts(comp, edges)
        target  = ", ".join(impacts) if impacts else "依存コンポーネント"

        delta = ev["delta"]
        reason = generate_reason(comp, delta, target)
        confidence = calc_confidence(chain, all_verified)

        seq += 1
        entry = {
            "cause_id":    f"RC_{seq:06d}",
            "component":   comp,
            "event_id":    ev["event_id"],
            "date":        today_str,
            "reason":      reason,
            "cause_chain": chain,
            "confidence":  confidence,
            "source":      "auto",
            "verified":    False,
        }
        new_entries.append(entry)

    if new_entries:
        ROOT_CAUSE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(ROOT_CAUSE_PATH, "a", encoding="utf-8") as f:
            for entry in new_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"[root_cause_engine] {len(new_entries)}件記録（本日合計: {len(done_comps) + len(new_entries)}件）")
    for entry in new_entries:
        print(f"  {entry['cause_id']}  {entry['component']}  conf={entry['confidence']}")
        print(f"    {entry['reason']}")
        print(f"    chain: {' → '.join(entry['cause_chain'])}")

    return new_entries


if __name__ == "__main__":
    run()
