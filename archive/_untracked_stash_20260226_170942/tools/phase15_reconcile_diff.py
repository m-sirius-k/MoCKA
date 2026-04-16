import argparse
import json
import os
import re
import sqlite3
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DICT = os.path.join(ROOT, "docs", "PHASE15_PROOF_DICTIONARY.md")
DEFAULT_PROOF_DB = os.path.join(ROOT, "audit", "ed25519", "audit.db")


@dataclass
class EventDef:
    event_type: str
    target_table: Optional[str]
    expected_columns: List[str]


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def normalize_md(md: str) -> str:
    md = re.sub(r"\\([#*\-])", r"\1", md)
    md = md.replace("\\_", "_")
    md = md.replace("竊・", " ")
    return md


def extract_event_blocks(md: str) -> List[Tuple[str, str]]:
    marker = re.compile(r"(?im)^(?:\s*#+\s*)?event_type\s*[:=]\s*([A-Za-z0-9_.\-/]+)\s*$")
    matches = list(marker.finditer(md))
    if not matches:
        return []
    blocks: List[Tuple[str, str]] = []
    for i, m in enumerate(matches):
        et = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        blocks.append((et, md[start:end]))
    return blocks


def parse_target_table(body: str) -> Optional[str]:
    patterns = [
        r"(?im)^\s*Target\s+Table:\s*\n\s*([A-Za-z0-9_]+)\s*$",
        r"(?im)^\s*Target\s+proof\s+table:\s*\n\s*([A-Za-z0-9_]+)\s*$",
        r"(?im)^\s*Target\s+proof\s+table:\s*([A-Za-z0-9_]+)\s*$",
        r"(?im)^\s*Target\s+Table:\s*([A-Za-z0-9_]+)\s*$",
    ]
    for pat in patterns:
        m = re.search(pat, body)
        if m:
            return m.group(1).strip()
    return None


def parse_expected_columns(body: str) -> List[str]:
    header_pats = [
        r"(?im)^\s*Deterministic\s+Structure:\s*$",
        r"(?im)^\s*Deterministic\s+row\s+structure:\s*$",
        r"(?im)^\s*Deterministic\s+row\s+structure\s*$",
        r"(?im)^\s*Deterministic\s+row:\s*$",
        r"(?im)^\s*Deterministic\s+row\s*$",
    ]
    m = None
    for hp in header_pats:
        m = re.search(hp, body)
        if m:
            break
    if not m:
        return []

    tail = body[m.end():]
    cols: List[str] = []

    for line in tail.splitlines():
        t = line.strip()
        if t == "":
            continue
        if re.match(r"(?i)^[A-Za-z].*:\s*$", t):
            break
        if t.startswith("- ") or t.startswith("* ") or t.startswith("• "):
            item = t[2:].strip()
            name = item.split("(", 1)[0].strip()
            if name:
                cols.append(name)
            continue
        if cols:
            break

    return cols


def load_dictionary(dict_path: str) -> Dict[str, EventDef]:
    md = normalize_md(read_text(dict_path))
    blocks = extract_event_blocks(md)
    out: Dict[str, EventDef] = {}
    for et, body in blocks:
        out[et] = EventDef(
            event_type=et,
            target_table=parse_target_table(body),
            expected_columns=parse_expected_columns(body),
        )
    return out


def sqlite_table_exists(conn: sqlite3.Connection, table: str) -> bool:
    cur = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE name=? AND type IN ('table','view')",
        (table,),
    )
    return cur.fetchone() is not None


def sqlite_table_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    cur = conn.execute(f"PRAGMA table_info({table})")
    rows = cur.fetchall()
    return [r[1] for r in rows]


def build_schema_diff(expected: List[str], actual: List[str]) -> Dict[str, List[str]]:
    exp_set = set(expected)
    act_set = set(actual)
    missing = [c for c in expected if c not in act_set]
    extra = [c for c in actual if c not in exp_set]
    common = [c for c in expected if c in act_set]
    return {"missing": missing, "extra": extra, "common": common}


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase15: dictionary-driven proof DB schema diff (READ ONLY)")
    ap.add_argument("--dict", dest="dict_path", default=DEFAULT_DICT)
    ap.add_argument("--proof-db", dest="proof_db", default=DEFAULT_PROOF_DB)
    ap.add_argument("--event-type", dest="event_type", default=None)
    ap.add_argument("--list", dest="list_only", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.dict_path):
        print(json.dumps({"status": "NG", "error": "dictionary_not_found", "path": args.dict_path}, indent=2))
        return 2

    d = load_dictionary(args.dict_path)

    if args.list_only:
        print(json.dumps({
            "status": "OK",
            "dictionary_path": os.path.relpath(args.dict_path, ROOT),
            "event_types": sorted(d.keys()),
            "count": len(d),
        }, indent=2))
        return 0

    if not args.event_type:
        print(json.dumps({"status": "NG", "error": "event_type_required", "hint": "run --list"}, indent=2))
        return 2

    if args.event_type not in d:
        print(json.dumps({
            "status": "NG",
            "error": "event_type_not_in_dictionary",
            "event_type": args.event_type,
            "known_event_types": sorted(d.keys()),
        }, indent=2))
        return 2

    if not os.path.exists(args.proof_db):
        print(json.dumps({"status": "NG", "error": "proof_db_not_found", "path": args.proof_db}, indent=2))
        return 2

    ev = d[args.event_type]
    if not ev.target_table:
        print(json.dumps({"status": "NG", "error": "target_table_missing_in_dictionary", "event_type": ev.event_type}, indent=2))
        return 2

    conn = sqlite3.connect(f"file:{args.proof_db}?mode=ro", uri=True)
    try:
        exists = sqlite_table_exists(conn, ev.target_table)
        if not exists:
            out = {
                "status": "NG",
                "error": "target_table_missing_in_proof_db",
                "dictionary_path": os.path.relpath(args.dict_path, ROOT),
                "proof_db_path": os.path.relpath(args.proof_db, ROOT),
                "event_type": ev.event_type,
                "target_table": ev.target_table,
                "target_table_exists": False,
                "expected_columns": ev.expected_columns,
                "actual_columns": [],
                "diff": {"missing": ev.expected_columns, "extra": [], "common": []},
                "write_capability": "DISABLED_READ_ONLY",
            }
            print(json.dumps(out, indent=2))
            return 3

        actual_cols = sqlite_table_columns(conn, ev.target_table)
    except sqlite3.Error as e:
        print(json.dumps({
            "status": "NG",
            "error": "sqlite_error",
            "event_type": ev.event_type,
            "target_table": ev.target_table,
            "detail": str(e),
        }, indent=2))
        return 3
    finally:
        conn.close()

    diff = build_schema_diff(ev.expected_columns, actual_cols)

    out = {
        "status": "OK",
        "dictionary_path": os.path.relpath(args.dict_path, ROOT),
        "proof_db_path": os.path.relpath(args.proof_db, ROOT),
        "event_type": ev.event_type,
        "target_table": ev.target_table,
        "target_table_exists": True,
        "expected_columns": ev.expected_columns,
        "actual_columns": actual_cols,
        "diff": diff,
        "write_capability": "DISABLED_READ_ONLY",
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())