# NOTE: Shadow-only self-test. Does not modify Primary. Creates temp governance file with corrupted vocab block.
import os
import subprocess
import sys
import tempfile
import json
import re

def run(cmd, cwd):
    p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    out, err = p.communicate()
    return p.returncode, out, err

def main():
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    gov_src = os.path.join(repo, "governance", "SHADOW_REPORT_SCHEMA.md")
    if not os.path.isfile(gov_src):
        raise SystemExit("missing governance/SHADOW_REPORT_SCHEMA.md")

    s = open(gov_src, "r", encoding="utf-8", errors="replace").read()

    # extract FAIL_KIND vocab block and corrupt it (drop one token)
    m = re.search(r"(?ms)^##\s+FAIL_KIND vocabulary.*?\n(.*?)(^\#\#\s|\Z)", s)
    if not m:
        raise SystemExit("FAIL_KIND vocabulary block not found")

    block = m.group(1)
    lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
    # keep only token-like lines
    toks = [ln for ln in lines if re.fullmatch(r"[A-Z0-9_]+", ln)]
    if len(toks) < 2:
        raise SystemExit("too few vocab tokens to corrupt")

    # remove last token to force mismatch
    corrupted = "\n".join(toks[:-1]) + "\n"

    # rebuild document by replacing the token lines region with corrupted tokens
    # simplest: replace the first occurrence of the exact token block with corrupted token block
    orig_token_block = "\n".join(toks) + "\n"
    if orig_token_block not in s:
        raise SystemExit("token block not found as contiguous text")

    s2 = s.replace(orig_token_block, corrupted, 1)

    with tempfile.TemporaryDirectory() as td:
        gov_dir = os.path.join(td, "governance")
        os.makedirs(gov_dir, exist_ok=True)
        gov_dst = os.path.join(gov_dir, "SHADOW_REPORT_SCHEMA.md")
        open(gov_dst, "w", encoding="utf-8", newline="\n").write(s2)

        shadow_py = os.path.join(repo, "shadow", "verify_all_shadow.py")
        rc, out, err = run(
            [sys.executable, shadow_py, "--repo-root", td, "--primary", "verify_pack_v4_sample/verify_all_v4.py"],
            repo,
        )

        try:
            r = json.loads(out)
        except Exception as e:
            raise SystemExit(f"json parse failed: {type(e).__name__}: {e}")

        kinds = r.get("result", {}).get("fail", {}).get("kinds", [])
        if "VOCAB_MISMATCH" not in kinds:
            raise SystemExit(f"expected VOCAB_MISMATCH, got kinds={kinds}")

        print("OK: vocab mismatch self-test PASS")
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
