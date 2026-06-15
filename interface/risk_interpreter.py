"""
risk_interpreter.py -- TIC Risk Interpreter (Phase 1/2/3)

risk_scorer.py が計算した dependency_map.json を読み込み、各コンポーネントの
スコアに対して決定論的な "why"（根拠テキスト）を付与する。

- AI呼び出しなし。change_frequency / substitutability / blast_radius から
  固定のフレーズを組み合わせて生成する。
- override_metadata.json を読み、expires を過ぎていれば override を無効化し
  計算値（risk_score再計算）を採用する。
- risk_scorer.py のコア計算ロジック（calc_score）は変更しない。

Phase2/3: SYSTEM STATUS / Today's Changes / Risk Summary(差分付き) / Today's Focus
を順に表示する。risk_history.jsonl に日次スコアをappendし、前日比を計算する。
"""

import json
import datetime
import subprocess
import sys
import io
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from risk_scorer import calc_score, rank, FREQ_SCORE, SUBST_SCORE, blast_score, RESET
from graph_loader import load_edges, get_impacts

MAP_PATH      = Path("C:/Users/sirok/MoCKA/data/tic/dependency_map.json")
OVERRIDE_PATH = Path("C:/Users/sirok/MoCKA/data/tic/override_metadata.json")
HISTORY_PATH  = Path("C:/Users/sirok/MoCKA/data/tic/risk_history.jsonl")
EVENTS_PATH   = Path("C:/Users/sirok/MoCKA/data/tic/dependency_events.jsonl")
HEALTH_LOG    = Path("C:/Users/sirok/MoCKA/data/tic/health_log.jsonl")
WATCHER_QUEUE = Path("C:/Users/sirok/MoCKA/data/watcher_queue")
MOCKA_ROOT    = Path("C:/Users/sirok/MoCKA")

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"

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


# ── Phase2: 履歴・差分 ───────────────────────────────────────────────────────

def load_prev_scores() -> dict:
    """risk_history.jsonl の最後の行（今日以前の最新エントリ）からscoresを返す。"""
    if not HISTORY_PATH.exists():
        return {}
    today_str = datetime.date.today().isoformat()
    last_other = None
    with open(HISTORY_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except Exception:
                continue
            if entry.get("date") != today_str:
                last_other = entry
    if last_other:
        return last_other.get("scores", {})
    return {}


def save_history(results: list):
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "date":   datetime.date.today().isoformat(),
        "scores": {r["component"]: r["score"] for r in results},
    }
    with open(HISTORY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def diff_str(curr: int, prev) -> str:
    if prev is None:
        return "(=)"
    delta = curr - prev
    if delta == 0:
        return "(=)"
    if delta > 0:
        return f"(▲+{delta})"
    return f"(▼{delta})"


# ── Phase2: Trace Layer ──────────────────────────────────────────────────────

def _load_events_today() -> list:
    today_str = datetime.date.today().isoformat()
    if not EVENTS_PATH.exists():
        return []
    out = []
    with open(EVENTS_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except Exception:
                continue
            if entry.get("date") == today_str:
                out.append(entry)
    return out


def trace_events(results: list, prev_scores: dict) -> list:
    """前日比でスコア変化があったコンポーネントを dependency_events.jsonl に記録する。
    同日・同コンポーネントの記録が既にある場合は冪等性のためスキップする。"""
    today_str  = datetime.date.today().isoformat()
    existing   = _load_events_today()
    done_comps = {e["component"] for e in existing}
    seq        = len(existing)

    new_entries = []
    for r in results:
        comp = r["component"]
        if comp in done_comps:
            continue
        prev = prev_scores.get(comp)
        if prev is None:
            continue
        delta = r["score"] - prev
        if delta == 0:
            continue

        rank_prev, _ = rank(prev)
        rank_new     = r["rank"]

        seq += 1
        entry = {
            "event_id":     f"DE_{today_str.replace('-', '')}_{seq:03d}",
            "date":         today_str,
            "component":    comp,
            "prev_score":   prev,
            "new_score":    r["score"],
            "delta":        delta,
            "rank_prev":    rank_prev,
            "rank_new":     rank_new,
            "rank_changed": rank_prev != rank_new,
            "source":       "risk_interpreter",
            "verified":     False,
        }
        new_entries.append(entry)

    if new_entries:
        EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(EVENTS_PATH, "a", encoding="utf-8") as f:
            for entry in new_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return existing + new_entries


def print_trace_log(events_today: list):
    print("=" * 50)
    print("  Trace Log  (本日)")
    print("=" * 50)
    if not events_today:
        print("  No changes detected.")
    else:
        width = max(len(e["component"]) for e in events_today)
        for e in events_today:
            d = e["delta"]
            d_str = f"▲+{d}" if d > 0 else f"▼{d}"
            print(
                f"  {e['component']:<{width}}  {e['prev_score']:>3} → {e['new_score']:>3}  "
                f"({d_str})  {e['rank_prev']} → {e['rank_new']}"
            )
    print("=" * 50)
    print()


# ── Phase2: SYSTEM STATUS ──────────────────────────────────────────────────

def system_status() -> list:
    checks = []

    # Health Check: health_log.jsonl の最新エントリの overall
    hc_ok = False
    if HEALTH_LOG.exists():
        try:
            with open(HEALTH_LOG, encoding="utf-8") as f:
                lines = [l for l in f if l.strip()]
            if lines:
                last = json.loads(lines[-1])
                hc_ok = last.get("overall") == "ALL PASS"
        except Exception:
            hc_ok = False
    checks.append(("Health Check", hc_ok))

    # Watcher: data/watcher_queue/ の存在確認で代替
    checks.append(("Watcher", WATCHER_QUEUE.exists()))

    # Git Sync: git status --porcelain が空ならOK
    git_ok = False
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(MOCKA_ROOT), capture_output=True, text=True, timeout=10,
        )
        git_ok = (r.returncode == 0 and r.stdout.strip() == "")
    except Exception:
        git_ok = False
    checks.append(("Git Sync", git_ok))

    # UTF-8: このファイル自身をstrict utf-8で読めるか
    utf8_ok = True
    try:
        Path(__file__).read_text(encoding="utf-8")
    except Exception:
        utf8_ok = False
    checks.append(("UTF-8", utf8_ok))

    return checks


def print_system_status(checks: list):
    today = datetime.date.today()
    print("=" * 50)
    print(f"  SYSTEM STATUS  {today}")
    print("=" * 50)
    for name, ok in checks:
        status = f"{GREEN}OK{RESET}" if ok else f"{RED}FAIL{RESET}"
        print(f"  {name:<15} {status}")
    print("=" * 50)
    print()


# ── Phase3: Today's Changes / Today's Focus ─────────────────────────────────

def print_todays_changes(events_today: list):
    new_critical_events = [e for e in events_today
                            if e["rank_changed"] and e["rank_new"] == "CRITICAL"]
    risk_up_events   = [e for e in events_today if e["delta"] > 0]
    risk_down_events = [e for e in events_today if e["delta"] < 0]
    rank_changed     = [e for e in events_today if e["rank_changed"]]

    print("=" * 50)
    print("  Today's Changes")
    print("=" * 50)

    if new_critical_events:
        e = new_critical_events[0]
        extra = f"  ({e['component']} {e['rank_prev']}→{e['rank_new']})"
    else:
        extra = ""
    print(f"  NEW Critical : {len(new_critical_events)}{extra}")

    if risk_up_events:
        e = risk_up_events[0]
        extra = f"  ({e['component']} {e['prev_score']}→{e['new_score']} +{e['delta']})"
    else:
        extra = ""
    print(f"  Risk Up      : {len(risk_up_events)}{extra}")

    print(f"  Risk Down    : {len(risk_down_events)}")
    print(f"  Rank Changed : {len(rank_changed)}")
    print("=" * 50)
    print()

    up_items = [(e["component"], e["prev_score"], e["new_score"]) for e in risk_up_events]
    return {
        "new_critical": len(new_critical_events),
        "risk_up":      len(risk_up_events),
        "risk_down":    len(risk_down_events),
        "up_items":     up_items,
    }


def print_todays_focus(results: list, changes: dict):
    print("=" * 50)
    print("  Today's Focus")
    print("=" * 50)

    if changes["risk_up"] == 0 and changes["new_critical"] == 0:
        top = results[0]
        prev_unchanged = "unchanged"
        print("  No new technical risks detected.")
        print(f"  Highest risk: {top['component']} ({top['score']}, {prev_unchanged})")
        print("  Action required: None")
    else:
        if changes["up_items"]:
            comp, prev, score = changes["up_items"][0]
            r = next(x for x in results if x["component"] == comp)
            print(f"  Risk increased: {comp}  {prev} → {score} (+{score - prev})")
            print(f"  Reason: {r['why']}")
            print(f"  Recommended action: {comp} の最新仕様変更を確認してください")
        else:
            crit = next((x for x in results if x["rank"] == "CRITICAL"), results[0])
            print(f"  New critical component: {crit['component']} ({crit['score']})")
            print(f"  Reason: {crit['why']}")
            print(f"  Recommended action: {crit['component']} を優先確認してください")

    print("=" * 50)
    print()


# ── メイン ────────────────────────────────────────────────────────────────────

def run():
    if not MAP_PATH.exists():
        print(f"[ERROR] {MAP_PATH} not found")
        sys.exit(1)

    data      = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    overrides = load_overrides()
    today     = datetime.date.today()

    results = [interpret(dep, overrides, today) for dep in data["dependencies"]]
    results.sort(key=lambda r: r["score"], reverse=True)

    prev_scores = load_prev_scores()

    print()
    print_system_status(system_status())

    events_today = trace_events(results, prev_scores)
    changes = print_todays_changes(events_today)
    print_trace_log(events_today)

    width = max(len(r["component"]) for r in results)
    edges = load_edges()
    print("=" * 70)
    print(f"  Today's Technical Risk Summary  {today}")
    print("=" * 70)
    for r in results:
        d = diff_str(r["score"], prev_scores.get(r["component"]))
        impacts = get_impacts(r["component"], edges)
        impact_str = f"  → {', '.join(impacts)}" if impacts else ""
        print(
            f"  {r['component']:<{width}}  {r['_color']}{r['score']:>3} {d:<8}{RESET} "
            f"[{r['rank']:<8}]{RESET}  {r['why']}{impact_str}"
        )
    print("=" * 70)
    print()

    print_todays_focus(results, changes)

    save_history(results)

    return results


if __name__ == "__main__":
    run()
