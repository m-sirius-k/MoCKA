# NOTE: Caliber-only self-test. Ensures stdout/stderr sha256 are required and must be 64-hex.
import json
import os
import subprocess
import sys
import tempfile

def run(cmd, cwd):
    p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    out, err = p.communicate()
    return p.returncode, out, err

def main():
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    extractor = os.path.join(repo, "caliber", "extract_caliber_record.py")
    if not os.path.isfile(extractor):
        raise SystemExit("missing caliber/extract_caliber_record.py")

    fake = {
        "schema_version": "1.3.0",
        "report_id": "TEST_FAKE",
        "tool": {"name": "verify_all_shadow", "version": "X"},
        "primary_run": {"verifier": "X", "exit_code": 0},
        "working_tree": {"mutation_detected": False},
        "io": {"stdout": {"sha256": ""}, "stderr": {"sha256": ""}},
        "result": {"ok": True, "fail": {"kinds": [], "items": []}},
    }

    with tempfile.TemporaryDirectory() as td:
        p_shadow = os.path.join(td, "fake_shadow.json")
        with open(p_shadow, "w", encoding="utf-8", newline="\n") as f:
            json.dump(fake, f, ensure_ascii=False)

        p_out = os.path.join(td, "out.json")
        rc, out, err = run([sys.executable, extractor, "--repo-root", repo, "--shadow-report", p_shadow, "--out", p_out], repo)

        if rc == 0:
            raise SystemExit("expected non-zero exit code, got rc=0")

        combined = (out + "\n" + err).strip()
        if "TOOL_ERROR:" not in combined:
            raise SystemExit("expected TOOL_ERROR in output")

        print("OK: caliber hash required self-test PASS")
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
