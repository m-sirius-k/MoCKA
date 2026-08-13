"""
evaluator_dynamic_v2.py
JARVIS Fluid Coordinate with S-factor Integration

Extends evaluator_dynamic.py to include XYZ+TS model:
- X: Institutional Integrity
- Y: Record Quality
- Z: Governance Stability
- t: Timestamp
- S: Situational Influence Set {H,P,B,T,TC,SD,OC}
"""

import csv
import json
import math
from pathlib import Path
from datetime import datetime
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Local paths (Linux session adaptation)
BASE = Path("/home/user/MoCKA")
EVENTS_CSV = BASE / "data/events.csv"
TRAJECTORY_CSV = BASE / "data/trajectory.csv"
TRAJECTORY_V2_CSV = BASE / "data/trajectory_v2.csv"
RECURRENCE_CSV = BASE / "data/recurrence_registry.csv"
CONTEXT_VECTORS_JSONL = BASE / "data/context_vectors.jsonl"

PROTOCOL_KW = ["mocka_get_overview","mocka_get_todo","mocka_write_event",
               "mocka_update_todo","session_start","protocol"]

# ============================================================
# XYZ Calculation (existing logic, preserved)
# ============================================================

def calc_x(row):
    """X: Institutional Integrity (0-1)

    Measures system adherence to governance protocols.
    Higher when: MCP channel, human-initiated, protocol-compliant
    """
    s = 0.5
    ch = row.get("channel_type", "")
    ac = row.get("who_actor", "")
    fn = row.get("free_note", "").lower()
    ti = row.get("title", "").lower()

    if ch == "mcp":
        s += 0.4
    elif ac == "mocka_router":
        s += 0.1
    elif ac.startswith("human_"):
        s += 0.2

    if any(k in fn or k in ti for k in PROTOCOL_KW):
        s += 0.1
    if "session_end" in fn or "milestone" in fn:
        s += 0.1

    return round(min(s, 1.0), 3)


def calc_y(row):
    """Y: Record Quality (0-1)

    Measures completeness and clarity of event documentation.
    Higher when: proper event ID, descriptive titles, category A risk
    """
    s = 0.3
    eid = row.get("event_id", "")

    if eid.startswith("E2") and "_" in eid and not eid.endswith("_auto"):
        s += 0.3
    elif eid.endswith("_auto"):
        s += 0.1

    if len(row.get("title", "")) > 5:
        s += 0.15
    if len(row.get("short_summary", "")) > 10:
        s += 0.1

    cat = row.get("category_ab", "")
    if cat == "A":
        s += 0.1
    elif cat == "B":
        s -= 0.1

    risk = row.get("risk_level", "")
    if risk == "normal":
        s += 0.05
    elif risk in ("high", "critical"):
        s -= 0.2

    return round(min(max(s, 0.0), 1.0), 3)


def calc_z(row, rc):
    """Z: Governance Stability (0-1)

    Measures incident rate and system recovery.
    Higher when: no incidents, fixed issues
    """
    s = 1.0
    fn = row.get("free_note", "").lower()

    if "incident" in fn:
        s -= 0.3
    if "error" in fn or "fail" in fn:
        s -= 0.2
    if "fixed" in fn or "restored" in fn:
        s += 0.1

    c = rc.get(row.get("what_type", ""), 0)
    if c >= 10:
        s -= 0.4
    elif c >= 5:
        s -= 0.25
    elif c >= 3:
        s -= 0.1

    return round(min(max(s, 0.0), 1.0), 3)


# ============================================================
# S-factor Integration (NEW)
# ============================================================

def load_context_vectors() -> dict:
    """Load pre-computed context vectors from context_vectors.jsonl

    Returns: {timestamp: S_vector_dict}
    """
    s_cache = {}
    if not CONTEXT_VECTORS_JSONL.exists():
        return s_cache

    try:
        with open(CONTEXT_VECTORS_JSONL, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    ts = record.get('timestamp')
                    if ts:
                        s_cache[ts] = record.get('S_vector', {})
                except:
                    pass
    except Exception as e:
        print(f"[WARN] Could not load context vectors: {e}")

    return s_cache


def get_s_vector(timestamp: str, s_cache: dict) -> dict:
    """Get S vector for timestamp, or return default neutral values"""
    if timestamp in s_cache:
        return s_cache[timestamp]

    # Default neutral S vector (all 0.5)
    return {
        'H_historical': 0.5,
        'P_political': 0.5,
        'B_budget': 0.5,
        'T_timeline': 0.5,
        'TC_technical': 0.75,
        'SD_social': 0.6,
        'OC_organizational': 0.7,
    }


def calc_s_mean(s_vec: dict) -> float:
    """Calculate mean of S factors"""
    factors = [
        s_vec.get('H_historical', 0.5),
        s_vec.get('P_political', 0.5),
        s_vec.get('B_budget', 0.5),
        s_vec.get('T_timeline', 0.5),
        s_vec.get('TC_technical', 0.75),
        s_vec.get('SD_social', 0.6),
        s_vec.get('OC_organizational', 0.7),
    ]
    return round(sum(factors) / len(factors), 3)


def calc_s_variance(s_vec: dict) -> float:
    """Calculate variance of S factors (uncertainty indicator)"""
    factors = [
        s_vec.get('H_historical', 0.5),
        s_vec.get('P_political', 0.5),
        s_vec.get('B_budget', 0.5),
        s_vec.get('T_timeline', 0.5),
        s_vec.get('TC_technical', 0.75),
        s_vec.get('SD_social', 0.6),
        s_vec.get('OC_organizational', 0.7),
    ]
    mean = sum(factors) / len(factors)
    variance = sum((f - mean) ** 2 for f in factors) / len(factors)
    return round(variance, 4)


# ============================================================
# Deviation Classification (existing)
# ============================================================

def layer1(row):
    """Deviation classification from event attributes"""
    fn = row.get("free_note", "").lower()
    ti = row.get("title", "").lower()
    wt = row.get("what_type", "")

    if "上書き" in ti or "overwrite" in fn or ("incident" in fn and "chatgpt" in fn):
        return {"category": "VIOLATION", "deviation_type": "INSTRUCTION_IGNORE"}
    if wt == "save" and row.get("who_actor") == "mocka_router":
        return {"category": "OK", "deviation_type": None}
    if row.get("event_id", "").endswith("_auto") and row.get("channel_type") == "mcp":
        return {"category": "VIOLATION", "deviation_type": "FORMAT_COLLAPSE"}
    if "hash" in fn and ("mismatch" in fn or "broken" in fn):
        return {"category": "VIOLATION", "deviation_type": "DEPENDENCY_BREAK"}

    return {"category": "OK", "deviation_type": None}


def calc_conf(n, x, y, z, s_mean=0.5):
    """Confidence score with S-factor adjustment

    Higher confidence when: more samples, coordinates near ideal (0.7),
    Z near 1.0, and S_mean high (stable context)
    """
    if n == 0:
        return 0.1

    base = min(0.9, math.log(n + 1) / math.log(100))
    cons = 1.0 - (abs(x - 0.7) + abs(y - 0.7) + abs(1.0 - z)) / 3.0
    s_factor = 0.5 + (s_mean * 0.5)  # S stability boosts confidence

    return round(max(0.1, min(1.0, base * 0.5 + cons * 0.3 + s_factor * 0.2)), 3)


def load_rc():
    """Load recurrence counts by event type"""
    rc = {}
    if not RECURRENCE_CSV.exists():
        return rc
    try:
        with open(RECURRENCE_CSV, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                k = row.get("what_type") or row.get("event_type") or ""
                if k:
                    rc[k] = rc.get(k, 0) + 1
    except:
        pass
    return rc


# ============================================================
# Build trajectory with S-factors
# ============================================================

HDR_V2 = [
    "timestamp", "event_id", "who_actor", "what_type",
    "X", "Y", "Z",  # Institutional coordinates
    "S_mean", "S_variance",  # Situational influence aggregates
    "H_historical", "P_political", "B_budget", "T_timeline",  # S factors
    "TC_technical", "SD_social", "OC_organizational",
    "category", "deviation_type", "confidence", "coordinate_state"
]


def build_v2():
    """Build trajectory.csv with XYZ+TS model"""
    print("=" * 60)
    print("MoCKA evaluator_dynamic_v2.py")
    print("trajectory_v2.csv 構築開始 (with S-factor integration)")
    print("=" * 60)

    rc = load_rc()
    s_cache = load_context_vectors()
    rows = []
    n = 0

    try:
        with open(EVENTS_CSV, encoding="utf-8", errors="replace") as f:
            for row in csv.DictReader(f):
                timestamp = row.get("when", "")
                x = calc_x(row)
                y = calc_y(row)
                z = calc_z(row, rc)

                s_vec = get_s_vector(timestamp, s_cache)
                s_mean = calc_s_mean(s_vec)
                s_variance = calc_s_variance(s_vec)

                j = layer1(row)
                conf = calc_conf(n, x, y, z, s_mean)

                rows.append({
                    "timestamp": timestamp,
                    "event_id": row.get("event_id", ""),
                    "who_actor": row.get("who_actor", ""),
                    "what_type": row.get("what_type", ""),
                    "X": x,
                    "Y": y,
                    "Z": z,
                    "S_mean": s_mean,
                    "S_variance": s_variance,
                    "H_historical": round(s_vec.get('H_historical', 0.5), 3),
                    "P_political": round(s_vec.get('P_political', 0.5), 3),
                    "B_budget": round(s_vec.get('B_budget', 0.5), 3),
                    "T_timeline": round(s_vec.get('T_timeline', 0.5), 3),
                    "TC_technical": round(s_vec.get('TC_technical', 0.75), 3),
                    "SD_social": round(s_vec.get('SD_social', 0.6), 3),
                    "OC_organizational": round(s_vec.get('OC_organizational', 0.7), 3),
                    "category": j["category"],
                    "deviation_type": j["deviation_type"] or "",
                    "confidence": conf,
                    "coordinate_state": json.dumps({
                        "X": x, "Y": y, "Z": z,
                        "S_mean": s_mean,
                        "n": n
                    })
                })
                n += 1

        # Write trajectory v2
        with open(TRAJECTORY_V2_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=HDR_V2)
            w.writeheader()
            w.writerows(rows)

        # Statistics
        ok = sum(1 for r in rows if r["category"] == "OK")
        vio = sum(1 for r in rows if r["category"] == "VIOLATION")
        ax = round(sum(float(r["X"]) for r in rows) / n, 3) if n > 0 else 0
        ay = round(sum(float(r["Y"]) for r in rows) / n, 3) if n > 0 else 0
        az = round(sum(float(r["Z"]) for r in rows) / n, 3) if n > 0 else 0
        as_mean = round(sum(float(r["S_mean"]) for r in rows) / n, 3) if n > 0 else 0

        print(f"\n処理件数: {n}")
        print(f"OK: {ok}, VIOLATION: {vio}")
        print(f"\n座標平均値:")
        print(f"  X (Institutional Integrity):  {ax}")
        print(f"  Y (Record Quality):           {ay}")
        print(f"  Z (Governance Stability):     {az}")
        print(f"  S_mean (Situational Context): {as_mean}")
        print(f"\n書出完了: {TRAJECTORY_V2_CSV}")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Build failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    build_v2()
