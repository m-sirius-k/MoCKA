# C:\Users\sirok\MoCKA\tools\phase14_6_audit_check.py
# note: Phase14.6 one-shot audit check (Proof + Governance + CSV)

import os
import subprocess
import sys

ROOT = r"C:\Users\sirok\MoCKA"

GOV_VERIFY = os.path.join(ROOT, "audit", "ed25519", "governance", "governance_chain_verify.py")
PROOF_REPORT = os.path.join(ROOT, "tools", "phase14_branch_guard_report.py")

CHANGE_LOG = os.path.join(ROOT, "audit", "ed25519", "governance", "change_log.csv")
IMPACT_REG = os.path.join(ROOT, "audit", "ed25519", "governance", "impact_registry.csv")
BACKUP_IDX = os.path.join(ROOT, "audit", "ed25519", "governance", "backup_index.csv")

def tail(path: str, n: int) -> str:
    if not os.path.exists(path):
        return "MISSING: " + path
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.read().replace("\r\n", "\n").replace("\r", "\n").split("\n")
    lines = [x for x in lines if x.strip()]
    return "\n".join(lines[-n:])

def run_py(path: str) -> int:
    if not os.path.exists(path):
        print("MISSING:", path)
        return 2
    r = subprocess.run([sys.executable, path], cwd=ROOT)
    return r.returncode

def main() -> int:
    print("=== Phase14.6 Audit Check ===")
    print("note: Proof+Governance+Human-readable quick verification")
    print("ROOT:", ROOT)
    print("")

    print("[1] Governance chain verify")
    rc1 = run_py(GOV_VERIFY)
    print("RC:", rc1)
    print("")

    print("[2] Proof branch guard report")
    rc2 = run_py(PROOF_REPORT)
    print("RC:", rc2)
    print("")

    print("[3] CSV tails")
    print("--- change_log.csv (tail 5) ---")
    print(tail(CHANGE_LOG, 5))
    print("")
    print("--- impact_registry.csv (tail 5) ---")
    print(tail(IMPACT_REG, 5))
    print("")
    print("--- backup_index.csv (tail 5) ---")
    print(tail(BACKUP_IDX, 5))
    print("")

    if rc1 == 0 and rc2 == 0:
        print("OK: Phase14.6 audit check passed")
        return 0

    print("FAIL: check return codes")
    return 2

if __name__ == "__main__":
    raise SystemExit(main())