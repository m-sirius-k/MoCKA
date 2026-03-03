# NOTE: Caliber-only self-test. Does not modify Primary or Shadow artifacts.
# It creates a temporary governance/CALIBER_RECORD_SCHEMA.md with a mismatched schema_version
# and asserts that extract_caliber_record.py fails with TOOL_ERROR.

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
        raise SystemExit("missing outbox/shadow_last.json (run Shadow once and save it before this test)")

    extractor = os.path.join(repo, "caliber", "extract_caliber_record.py")
    if not os.path.isfile(extractor):
        raise SystemExit("missing caliber/extract_caliber_record.py")

    with tempfile.TemporaryDirectory() as td:
        gov_dir = os.path.join(td, "governance")
        out_dir = os.path.join(td, "outbox")
        os.makedirs(gov_dir, exist_ok=True)
        os.makedirs(out_dir, exist_ok=True)

        # create intentionally mismatched governance schema file
        gov_path = os.path.join(gov_dir, "CALIBER_RECORD_SCHEMA.md")
        open(gov_path, "w", encoding="utf-8", newline="\n").write(
            "# CALIBER_RECORD_SCHEMA (Frozen Contract)\n\n"
            "schema_version: 9.9.9\n"
        )

        out_path = os.path.join(out_dir, "caliber_last.json")

        rc, out, err = run(
            [sys.executable, extractor, "--repo-root", td, "--shadow-report", src_shadow, "--out", out_path],
            repo,
        )

        # extractor should fail (non-zero) and mention TOOL_ERROR
        if rc == 0:
            raise SystemExit("expected non-zero exit code, got rc=0")

        combined = (out + "\n" + err).strip()
        if "TOOL_ERROR:" not in combined:
            raise SystemExit("expected TOOL_ERROR in output")

        print("OK: caliber schema mismatch self-test PASS")
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
