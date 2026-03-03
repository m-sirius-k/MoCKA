# NOTE: Caliber-only self-test. Ensures summary is present and derived without raw text.
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
    src_shadow = os.path.join(repo, "outbox", "shadow_last.json")
    if not os.path.isfile(src_shadow):
        raise SystemExit("missing outbox/shadow_last.json")

    extractor = os.path.join(repo, "caliber", "extract_caliber_record.py")
    if not os.path.isfile(extractor):
        raise SystemExit("missing caliber/extract_caliber_record.py")

    with tempfile.TemporaryDirectory() as td:
        out_path = os.path.join(td, "caliber.json")
        rc, out, err = run([sys.executable, extractor, "--repo-root", repo, "--shadow-report", src_shadow, "--out", out_path], repo)
        if rc != 0:
            raise SystemExit("extractor failed")

        r = json.load(open(out_path, "r", encoding="utf-8"))
        s = r.get("signals", {}).get("summary", "")
        if not isinstance(s, str) or not s.strip():
            raise SystemExit("missing signals.summary")

        # must not contain raw sentinel words from primary output (cheap guard)
        if "verify_all_v4" in s or "OK:" in s or "FAIL" in s:
            raise SystemExit("summary appears to contain raw output text")

        print("OK: caliber summary self-test PASS")
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
