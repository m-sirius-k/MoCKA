# NOTE: Caliber extractor is derived artifact generation. It must not modify Primary or Shadow.
# Input: Shadow report JSON (schema v1.3.0)
# Output: Caliber record JSON (schema v0.1.0) - minimal, stable, machine-friendly.

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone

CALIBER_SCHEMA_VERSION = "0.1.0"

def sha256_text(t: str) -> str:
    h = hashlib.sha256()
    h.update(t.encode("utf-8"))
    return h.hexdigest()

def utc_now_rfc3339() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8", errors="strict") as f:
        return json.load(f)

def deterministic_dump(obj: dict) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"

def parse_args(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--shadow-report", required=True)
    ap.add_argument("--out", default="")
    return ap.parse_args(argv)

def main(argv):
    a = parse_args(argv)
    r = load_json(a.shadow_report)

    # Minimal stable fields
    record = {
        "schema_version": CALIBER_SCHEMA_VERSION,
        "generated_at_utc": utc_now_rfc3339(),
        "source": {
            "shadow_report_id": r.get("report_id", ""),
            "shadow_schema_version": r.get("schema_version", ""),
            "shadow_tool": r.get("tool", {}),
            "primary_verifier": r.get("primary_run", {}).get("verifier", ""),
            "primary_exit_code": r.get("primary_run", {}).get("exit_code", None),
        },
        "signals": {
            "ok": bool(r.get("result", {}).get("ok", False)),
            "fail_kinds": list(r.get("result", {}).get("fail", {}).get("kinds", [])),
            "mutation_detected": bool(r.get("working_tree", {}).get("mutation_detected", False)),
            "stdout_sha256": r.get("io", {}).get("stdout", {}).get("sha256", ""),
            "stderr_sha256": r.get("io", {}).get("stderr", {}).get("sha256", ""),
        },
        "evidence": [],
    }

    # Evidence normalization: keep kind + evidence payload hashes only (no raw text)
    items = r.get("result", {}).get("fail", {}).get("items", [])
    for it in items:
        kind = str(it.get("kind", ""))
        ev = it.get("evidence", {})
        # stable representation of evidence
        ev_json = json.dumps(ev, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        record["evidence"].append({
            "kind": kind,
            "evidence_sha256": sha256_text(ev_json),
        })

    out_text = deterministic_dump(record)

    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as f:
            f.write(out_text)
    else:
        sys.stdout.write(out_text)

    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
