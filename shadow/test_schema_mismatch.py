# NOTE: Shadow-only self-test. Does not modify Primary. Creates temp governance file in shadow sandbox.
import os
import shutil
import subprocess
import sys
import tempfile
import json

def run(cmd, cwd):
    p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    out, err = p.communicate()
    return p.returncode, out, err

def main():
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    gov_src = os.path.join(repo, "governance", "SHADOW_REPORT_SCHEMA.md")
    if not os.path.isfile(gov_src):
        raise SystemExit("missing governance/SHADOW_REPORT_SCHEMA.md")

    with tempfile.TemporaryDirectory() as td:
        # shadow sandbox layout
        gov_dir = os.path.join(td, "governance")
        os.makedirs(gov_dir, exist_ok=True)
        gov_dst = os.path.join(gov_dir, "SHADOW_REPORT_SCHEMA.md")

        # copy real file then corrupt schema_version line
        s = open(gov_src, "r", encoding="utf-8", errors="replace").read()
        s = s.replace("schema_version: 1.2.0", "schema_version: 9.9.9")
        open(gov_dst, "w", encoding="utf-8", newline="\n").write(s)

        # run shadow with repo-root redirected to sandbox that contains corrupted governance doc
        shadow_py = os.path.join(repo, "shadow", "verify_all_shadow.py")
        rc, out, err = run([sys.executable, shadow_py, "--repo-root", td, "--primary", "verify_pack_v4_sample/verify_all_v4.py"], repo)

        # parse json output from stdout
        try:
            r = json.loads(out)
        except Exception as e:
            raise SystemExit(f"json parse failed: {type(e).__name__}: {e}")

        kinds = r.get("result", {}).get("fail", {}).get("kinds", [])
        if "SCHEMA_MISMATCH" not in kinds:
            raise SystemExit(f"expected SCHEMA_MISMATCH, got kinds={kinds}")

        print("OK: schema mismatch self-test PASS")
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
