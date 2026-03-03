# NOTE: Shadow is diagnostic-only. Primary is read-only. No repairs, no approvals, no exceptions.

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

SCHEMA_VERSION = "1.0.0"
TOOL_NAME = "verify_all_shadow"
TOOL_VERSION = "1.0.1"

FAIL_KIND_VOCAB = [
    "PRIMARY_FAILED",
    "MUTATION_DETECTED",
    "PRIMARY_STDERR",
    "PRIMARY_STDOUT_PATTERN",
    "TOOL_ERROR",
    "GIT_UNAVAILABLE",
    "UNKNOWN",
]

DEFAULT_PRIMARY_CANDIDATES = [
    "verify_all_v4.py",
    os.path.join("verify_pack_v4_sample", "verify_all_v4.py"),
    os.path.join("verify", "verify_all_v4.py"),
]

def utc_now_rfc3339():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def sha256_text(t):
    h = hashlib.sha256()
    h.update(t.encode("utf-8"))
    return h.hexdigest()

def sha256_lines(lines):
    return sha256_text("\n".join(lines) + "\n")

def run(cmd, cwd):
    t0 = time.time()
    p = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    out, err = p.communicate()
    dur_ms = int((time.time() - t0) * 1000)
    return p.returncode, out.splitlines(), err.splitlines(), dur_ms

def git_status_porcelain(cwd):
    try:
        rc, out, err, _ = run(["git", "status", "--porcelain"], cwd)
        if rc != 0:
            return False, "\n".join(err).strip()
        return True, "\n".join(out)
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

def lines_obj(lines):
    return {
        "lines": [{"n": i + 1, "text": lines[i]} for i in range(len(lines))],
        "sha256": sha256_lines(lines),
    }

def deterministic_dump(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"

def pick_primary(repo_root, explicit):
    if explicit:
        rel = explicit.replace("\\", "/")
        p = os.path.join(repo_root, rel)
        return rel if os.path.isfile(p) else ""
    for rel in DEFAULT_PRIMARY_CANDIDATES:
        p = os.path.join(repo_root, rel)
        if os.path.isfile(p):
            return rel
    return ""

def parse_args(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--primary", default="")
    ap.add_argument("--primary-args", default="")
    ap.add_argument("--stdout-pattern", default="")
    return ap.parse_args(argv)

def main(argv):
    args = parse_args(argv)
    repo_root = os.path.abspath(args.repo_root)

    primary_rel = pick_primary(repo_root, args.primary.strip())
    primary_args = [x for x in args.primary_args.split(" ") if x] if args.primary_args else []
    stdout_pattern = args.stdout_pattern if args.stdout_pattern else ""

    report = {}
    report["schema_version"] = SCHEMA_VERSION
    report["report_id"] = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    report["generated_at_utc"] = utc_now_rfc3339()
    report["tool"] = {"name": TOOL_NAME, "version": TOOL_VERSION}

    git_ok_before, status_before = git_status_porcelain(repo_root)
    clean_before = (status_before.strip() == "") if git_ok_before else False

    fails = []
    tool_error = ""

    if not git_ok_before:
        fails.append({"kind": "GIT_UNAVAILABLE", "message": f"git status failed (before): {status_before}"})

    if not primary_rel:
        tool_error = "primary verifier not found"
        rc = 99
        out_lines = []
        err_lines = [tool_error]
        dur_ms = 0
        primary_cmd = [sys.executable, "(missing)"]
    else:
        primary_cmd = [sys.executable, primary_rel] + primary_args
        try:
            rc, out_lines, err_lines, dur_ms = run(primary_cmd, repo_root)
        except Exception as e:
            tool_error = f"{type(e).__name__}: {e}"
            rc = 99
            out_lines = []
            err_lines = [tool_error]
            dur_ms = 0

    git_ok_after, status_after = git_status_porcelain(repo_root)
    clean_after = (status_after.strip() == "") if git_ok_after else False

    if not git_ok_after:
        fails.append({"kind": "GIT_UNAVAILABLE", "message": f"git status failed (after): {status_after}"})

    mutation = False
    if git_ok_before and git_ok_after:
        mutation = (status_before != status_after)

    if rc != 0:
        fails.append({"kind": "PRIMARY_FAILED", "message": f"exit_code={rc}"})

    if mutation:
        fails.append({"kind": "MUTATION_DETECTED", "message": "working-tree mutation detected (before != after)"})

    if err_lines:
        fails.append({"kind": "PRIMARY_STDERR", "message": "primary verifier wrote to stderr"})

    if stdout_pattern:
        hits = []
        for i, line in enumerate(out_lines, start=1):
            if stdout_pattern in line:
                hits.append({"n": i, "text_sha256": sha256_text(line)})
        if hits:
            fails.append({"kind": "PRIMARY_STDOUT_PATTERN", "message": f"stdout pattern matched: {stdout_pattern}", "evidence": {"hits": hits}})

    if tool_error:
        fails.append({"kind": "TOOL_ERROR", "message": tool_error})

    kind_rank = {k: i for i, k in enumerate(FAIL_KIND_VOCAB)}
    norm = []
    for f in fails:
        k = f.get("kind", "UNKNOWN")
        if k not in FAIL_KIND_VOCAB:
            k = "UNKNOWN"
        item = {"kind": k, "message": str(f.get("message", ""))}
        if "evidence" in f:
            item["evidence"] = f["evidence"]
        norm.append(item)

    distinct_kinds = sorted({x["kind"] for x in norm}, key=lambda k: kind_rank.get(k, 999))
    ok = (rc == 0) and (mutation is False) and (tool_error == "")

    report["primary_run"] = {
        "verifier": primary_rel if primary_rel else "",
        "mode": "read_only",
        "exit_code": rc,
        "duration_ms": dur_ms,
        "argv": primary_cmd,
    }

    report["working_tree"] = {
        "clean_before": bool(clean_before),
        "clean_after": bool(clean_after),
        "mutation_detected": bool(mutation),
        "status_before": status_before if git_ok_before else "",
        "status_after": status_after if git_ok_after else "",
    }

    report["io"] = {"stdout": lines_obj(out_lines), "stderr": lines_obj(err_lines)}

    report["result"] = {
        "ok": bool(ok),
        "fail": {
            "count": int(len(norm)),
            "kinds": distinct_kinds,
            "items": norm,
        },
    }

    sys.stdout.write(deterministic_dump(report))
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
