# NOTE: Caliber extractor is derived artifact generation. It must not modify Primary or Shadow.
# Input: Shadow report JSON (schema v1.x)
# Output: Caliber record JSON (schema v0.1.0) - minimal, stable, machine-friendly.

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone

CALIBER_SCHEMA_VERSION = "0.1.0"
GOV_SCHEMA_PATH = os.path.join("governance", "CALIBER_RECORD_SCHEMA.md")
GOV_SHADOW_SCHEMA_PATH = os.path.join("governance", "SHADOW_REPORT_SCHEMA.md")

# NOTE: Caliber fail_kinds must be a subset of Shadow FAIL_KIND vocabulary.
# This is closure: derived artifacts must not invent new failure kinds.
ALLOWED_FAIL_KINDS = [
    "PRIMARY_FAILED",
    "MUTATION_DETECTED",
    "PRIMARY_STDERR",
    "PRIMARY_STDOUT_PATTERN",
    "EXPECTED_FAIL_BUT_PASSED",
    "SCHEMA_MISMATCH",
    "VOCAB_MISMATCH",
    "TOOL_ERROR",
    "GIT_UNAVAILABLE",
    "UNKNOWN",
]

def sha256_text(t: str) -> str:
    h = hashlib.sha256()
    h.update(t.encode("utf-8"))
    return h.hexdigest()

def utc_now_rfc3339() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def deterministic_dump(obj: dict) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"

def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8", errors="strict") as f:
        return json.load(f)

def read_text(path: str) -> str:
    return open(path, "r", encoding="utf-8", errors="replace").read()

def extract_gov_schema_version(repo_root: str, rel_path: str) -> str:
    p = os.path.join(repo_root, rel_path)
    if not os.path.isfile(p):
        return ""
    s = read_text(p)
    m = re.search(r"(?m)^schema_version:\s*([0-9]+\.[0-9]+\.[0-9]+)\s*$", s)
    return m.group(1).strip() if m else ""

def extract_shadow_fail_kind_vocab(repo_root: str):
    p = os.path.join(repo_root, GOV_SHADOW_SCHEMA_PATH)
    if not os.path.isfile(p):
        return []

    s = read_text(p)
    m = re.search(r"(?ms)^##\s+FAIL_KIND vocabulary.*?\n(.*?)(^\#\#\s|\Z)", s)
    if not m:
        return []

    block = m.group(1)
    vocab = []
    for line in block.splitlines():
        t = line.strip()
        if not t:
            continue
        if re.fullmatch(r"[A-Z0-9_]+", t):
            vocab.append(t)
    return vocab

def parse_args(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--shadow-report", required=True)
    ap.add_argument("--out", default="")
    ap.add_argument("--repo-root", default=".")
    return ap.parse_args(argv)

def main(argv):
    a = parse_args(argv)
    repo_root = os.path.abspath(a.repo_root)

    gov_ver = extract_gov_schema_version(repo_root, GOV_SCHEMA_PATH)
    if not gov_ver:
        raise SystemExit("TOOL_ERROR: governance schema_version not found for CALIBER_RECORD_SCHEMA.md")
    if gov_ver != CALIBER_SCHEMA_VERSION:
        raise SystemExit(f"TOOL_ERROR: governance schema_version mismatch: governance={gov_ver} code={CALIBER_SCHEMA_VERSION}")

    # Phase 4-4 closure: ensure our ALLOWED_FAIL_KINDS matches governance Shadow FAIL_KIND vocabulary (subset rule baseline).
    shadow_vocab = extract_shadow_fail_kind_vocab(repo_root)
    if shadow_vocab:
        # We require ALLOWED_FAIL_KINDS == shadow_vocab for now to avoid silent divergence.
        if shadow_vocab != list(ALLOWED_FAIL_KINDS):
            raise SystemExit(
                "TOOL_ERROR: ALLOWED_FAIL_KINDS mismatch vs governance SHADOW_REPORT_SCHEMA.md FAIL_KIND vocabulary"
            )
    else:
        raise SystemExit("TOOL_ERROR: cannot read Shadow FAIL_KIND vocabulary from governance/SHADOW_REPORT_SCHEMA.md")

    r = load_json(a.shadow_report)

    fail_kinds = list(r.get("result", {}).get("fail", {}).get("kinds", []))
    bad = [k for k in fail_kinds if k not in ALLOWED_FAIL_KINDS]
    if bad:
        raise SystemExit("TOOL_ERROR: invalid fail_kinds detected (not in allowed Shadow vocabulary): " + ",".join(bad))

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
            "fail_kinds": fail_kinds,
            "mutation_detected": bool(r.get("working_tree", {}).get("mutation_detected", False)),
            "stdout_sha256": r.get("io", {}).get("stdout", {}).get("sha256", ""),
            "stderr_sha256": r.get("io", {}).get("stderr", {}).get("sha256", ""),
        },
        "evidence": [],
    }

    items = r.get("result", {}).get("fail", {}).get("items", [])
    for it in items:
        kind = str(it.get("kind", ""))
        ev = it.get("evidence", {})
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
