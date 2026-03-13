# NOTE: Shadow is diagnostic-only. Primary is read-only. No repairs, no approvals, no exceptions.

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone

SCHEMA_VERSION = "1.3.0"
TOOL_NAME = "verify_all_shadow"
TOOL_VERSION = "1.4.0"

HEAD_TAIL_LINES = 5  # NOTE: stdout trim window size
GOV_SCHEMA_PATH = os.path.join("governance", "SHADOW_REPORT_SCHEMA.md")

FAIL_KIND_VOCAB = [
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

def trim_stdout(lines, evidence_line_numbers):
    total = len(lines)
    if total <= HEAD_TAIL_LINES * 2:
        return lines, False, total

    head = list(range(0, HEAD_TAIL_LINES))
    tail = list(range(total - HEAD_TAIL_LINES, total))
    keep = set(head + tail + evidence_line_numbers)

    kept = []
    for i in sorted(keep):
        if 0 <= i < total:
            kept.append(lines[i])

    return kept, True, total

def read_text(path):
    return open(path, "r", encoding="utf-8", errors="replace").read()

def extract_gov_schema_version(repo_root):
    p = os.path.join(repo_root, GOV_SCHEMA_PATH)
    if not os.path.isfile(p):
        return ""
    s = read_text(p)
    m = re.search(r"(?m)^schema_version:\s*([0-9]+\.[0-9]+\.[0-9]+)\s*$", s)
    return m.group(1).strip() if m else ""

def extract_gov_vocab(repo_root):
    p = os.path.join(repo_root, GOV_SCHEMA_PATH)
    if not os.path.isfile(p):
        return []

    s = read_text(p)
    # find block starting at header, take subsequent non-empty non-header lines until next '## ' heading
    m = re.search(r"(?ms)^##\s+FAIL_KIND vocabulary.*?\n(.*?)(^\#\#\s|\Z)", s)
    if not m:
        return []

    block = m.group(1)
    vocab = []
    for line in block.splitlines():
        t = line.strip()
        if not t:
            continue
        if t.startswith("#"):
            continue
        # accept only UPPERCASE + digits + underscore tokens
        if re.fullmatch(r"[A-Z0-9_]+", t):
            vocab.append(t)
    return vocab

def parse_args(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--primary", default="")
    return ap.parse_args(argv)

def main(argv):
    args = parse_args(argv)
    repo_root = os.path.abspath(args.repo_root)

    report = {}
    report["schema_version"] = SCHEMA_VERSION
    report["report_id"] = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    report["generated_at_utc"] = utc_now_rfc3339()
    report["tool"] = {"name": TOOL_NAME, "version": TOOL_VERSION}

    git_ok_before, status_before = git_status_porcelain(repo_root)
    clean_before = (status_before.strip() == "") if git_ok_before else False

    fails = []
    tool_error = ""

    # Phase 3 closure checks: schema_version + vocabulary alignment
    gov_ver = extract_gov_schema_version(repo_root)
    if not gov_ver:
        fails.append({"kind": "SCHEMA_MISMATCH", "message": "governance schema_version not found"})
    elif gov_ver != SCHEMA_VERSION:
        fails.append({"kind": "SCHEMA_MISMATCH", "message": f"governance schema_version mismatch: governance={gov_ver} code={SCHEMA_VERSION}"})

    gov_vocab = extract_gov_vocab(repo_root)
    if not gov_vocab:
        fails.append({"kind": "VOCAB_MISMATCH", "message": "governance FAIL_KIND vocabulary block not found or empty"})
    else:
        code_vocab = list(FAIL_KIND_VOCAB)
        if gov_vocab != code_vocab:
            fails.append({
                "kind": "VOCAB_MISMATCH",
                "message": "FAIL_KIND vocabulary mismatch (order-sensitive)",
                "evidence": {
                    "governance_sha256": sha256_text("\n".join(gov_vocab) + "\n"),
                    "code_sha256": sha256_text("\n".join(code_vocab) + "\n"),
                },
            })

    primary_rel = pick_primary(repo_root, args.primary.strip())

    if not primary_rel:
        tool_error = "primary verifier not found"
        rc = 99
        out_lines = []
        err_lines = [tool_error]
        dur_ms = 0
        primary_cmd = [sys.executable, "(missing)"]
    else:
        primary_cmd = [sys.executable, primary_rel]
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

    if not git_ok_before:
        fails.append({"kind": "GIT_UNAVAILABLE", "message": f"git status failed (before): {status_before}"})
    if not git_ok_after:
        fails.append({"kind": "GIT_UNAVAILABLE", "message": f"git status failed (after): {status_after}"})

    mutation = False
    if git_ok_before and git_ok_after:
        mutation = (status_before != status_after)

    if rc != 0:
        fails.append({"kind": "PRIMARY_FAILED", "message": f"exit_code={rc}"})
    if mutation:
        fails.append({"kind": "MUTATION_DETECTED", "message": "working-tree mutation detected"})
    if err_lines:
        fails.append({"kind": "PRIMARY_STDERR", "message": "primary verifier wrote to stderr"})

    evidence_lines = []
    for i, line in enumerate(out_lines):
        if "EXPECTED_FAIL_BUT_PASSED" in line:
            evidence_lines.append(i)
            fails.append({
                "kind": "EXPECTED_FAIL_BUT_PASSED",
                "message": "expected fail but passed",
                "evidence": {"line": i + 1, "text_sha256": sha256_text(line)},
            })

    trimmed_out, trimmed_flag, total_lines = trim_stdout(out_lines, evidence_lines)

    kind_rank = {k: i for i, k in enumerate(FAIL_KIND_VOCAB)}
    kinds = sorted({f.get("kind", "UNKNOWN") for f in fails}, key=lambda k: kind_rank.get(k, 999))

    ok = (rc == 0) and (mutation is False) and (tool_error == "") and (len(fails) == 0)

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
    }

    report["io"] = {
        "stdout": {
            "lines": [{"n": i + 1, "text": trimmed_out[i]} for i in range(len(trimmed_out))],
            "sha256": sha256_lines(trimmed_out),
            "trimmed": bool(trimmed_flag),
            "total_lines": int(total_lines),
        },
        "stderr": {
            "lines": [{"n": i + 1, "text": err_lines[i]} for i in range(len(err_lines))],
            "sha256": sha256_lines(err_lines),
        },
    }

    report["result"] = {
        "ok": bool(ok),
        "fail": {
            "count": int(len(fails)),
            "kinds": kinds,
            "items": fails,
        },
    }

    sys.stdout.write(deterministic_dump(report))
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
