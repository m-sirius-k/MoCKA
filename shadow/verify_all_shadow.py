import json
import subprocess
import sys
import hashlib
import time
from datetime import datetime, timezone

SCHEMA_VERSION = "1.0.0"
TOOL_VERSION = "1.0.0"

FAIL_KIND = [
    "PRIMARY_FAILED",
    "MUTATION_DETECTED",
    "PRIMARY_STDERR",
    "PRIMARY_STDOUT_PATTERN",
    "TOOL_ERROR",
    "GIT_UNAVAILABLE",
    "UNKNOWN"
]

def sha256_text(t):
    h = hashlib.sha256()
    h.update(t.encode("utf-8"))
    return h.hexdigest()

def run(cmd):
    t0 = time.time()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    dur = int((time.time() - t0) * 1000)
    return p.returncode, out.splitlines(), err.splitlines(), dur

def git_status():
    try:
        rc, out, err, _ = run(["git","status","--porcelain"])
        if rc != 0:
            return False, ""
        return True, "\n".join(out)
    except:
        return False, ""

def main():
    report = {}
    report["schema_version"] = SCHEMA_VERSION
    report["report_id"] = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    report["generated_at_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    report["tool"] = {
        "name":"verify_all_shadow",
        "version":TOOL_VERSION
    }

    git_ok_before, status_before = git_status()

    rc, out_lines, err_lines, dur = run([sys.executable,"verify_all_v4.py"])

    git_ok_after, status_after = git_status()

    mutation = False
    if git_ok_before and git_ok_after:
        mutation = status_before != status_after

    fail_items = []

    if rc != 0:
        fail_items.append({"kind":"PRIMARY_FAILED","message":f"exit_code={rc}"})

    if mutation:
        fail_items.append({"kind":"MUTATION_DETECTED","message":"working tree changed"})

    if err_lines:
        fail_items.append({"kind":"PRIMARY_STDERR","message":"stderr detected"})

    ok = (rc == 0) and (mutation is False)

    report["primary_run"] = {
        "verifier":"verify_all_v4.py",
        "mode":"read_only",
        "exit_code":rc,
        "duration_ms":dur,
        "argv":[sys.executable,"verify_all_v4.py"]
    }

    report["working_tree"] = {
        "clean_before": status_before == "",
        "clean_after": status_after == "",
        "mutation_detected": mutation,
        "status_before": status_before,
        "status_after": status_after
    }

    report["io"] = {
        "stdout":{
            "lines":[{"n":i+1,"text":out_lines[i]} for i in range(len(out_lines))],
            "sha256":sha256_text("\n".join(out_lines)+"\n")
        },
        "stderr":{
            "lines":[{"n":i+1,"text":err_lines[i]} for i in range(len(err_lines))],
            "sha256":sha256_text("\n".join(err_lines)+"\n")
        }
    }

    report["result"] = {
        "ok":ok,
        "fail":{
            "count":len(fail_items),
            "kinds":sorted(list(set([f["kind"] for f in fail_items]))),
            "items":fail_items
        }
    }

    sys.stdout.write(json.dumps(report,sort_keys=True,separators=(",",":"))+"\n")

    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
