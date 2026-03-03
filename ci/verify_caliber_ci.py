import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INP  = ROOT / "outbox" / "shadow_e2e.utf8.json"
OUT1 = ROOT / "outbox" / "caliber_min_ci_run1.json"
OUT2 = ROOT / "outbox" / "caliber_min_ci_run2.json"

def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def run_once(out: Path):
    cmd = [
        sys.executable,
        str(ROOT / "caliber" / "run_caliber_min.py"),
        "--input", str(INP),
        "--output", str(out),
    ]
    r = subprocess.run(cmd)
    if r.returncode != 0:
        raise SystemExit(r.returncode)

def main():
    if not INP.exists():
        raise SystemExit(f"INPUT_NOT_FOUND={INP}")

    run_once(OUT1)
    run_once(OUT2)

    r1 = json.loads(OUT1.read_text(encoding="utf-8"))
    r2 = json.loads(OUT2.read_text(encoding="utf-8"))

    ks1 = set(r1.get("fail_kinds", []))
    ks2 = set(r2.get("fail_kinds", []))

    assert ks1 == {"EXPECTED_FAIL_BUT_PASSED"}, ks1
    assert ks2 == {"EXPECTED_FAIL_BUT_PASSED"}, ks2

    h1 = sha256(OUT1)
    h2 = sha256(OUT2)

    print("run1_sha256", h1)
    print("run2_sha256", h2)

    assert h1 == h2, "SHA256_MISMATCH"
    print("OK: CI caliber determinism + propagation verified")

if __name__ == "__main__":
    main()

# NOTE:
# - Verifies propagation and byte-level determinism
# - Input must be normalized UTF-8 no-BOM shadow output

