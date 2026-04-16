# NOTE: final_check_dict_driven_v1.py (Phase16 T12)
# NOTE: Purpose: dictionary-driven final check.
# NOTE: Reads invariant_catalog_v1.md, err_catalog_v1.md, state_machine_v1.yaml
# NOTE: Executes struct_verify_v1.py and requires PASS.
# NOTE: Any unmapped/undefined condition => FAIL.
# NOTE: Always emits verify_report_final_check_v1.json.

import os
import json
import subprocess
from datetime import datetime, timezone

BASE = r"C:\Users\sirok\MoCKA\governance_phase16_upgrade"
OUTBOX = r"C:\Users\sirok\MoCKA\outbox"

INV_PATH = os.path.join(BASE, "invariant_catalog_v1.md")
ERR_PATH = os.path.join(BASE, "err_catalog_v1.md")
SM_PATH  = os.path.join(BASE, "state_machine_v1.yaml")

STRUCT_VERIFIER = os.path.join(BASE, "struct_verify_v1.py")
STRUCT_REPORT = os.path.join(OUTBOX, "verify_report_struct_v1.json")

OUT_REPORT = os.path.join(OUTBOX, "verify_report_final_check_v1.json")

def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def read_text(p):
    with open(p, "r", encoding="utf-8") as f:
        return f.read()

def parse_err_codes(err_md: str):
    codes = set()
    for line in err_md.splitlines():
        line = line.strip()
        if line.startswith("ERR-") and ":" in line:
            codes.add(line.split(":")[0].strip())
    return codes

def parse_invariant_ids(inv_md: str):
    ids = set()
    for line in inv_md.splitlines():
        line = line.strip()
        if line.startswith("ID: "):
            ids.add(line.replace("ID:", "").strip())
    return ids

def parse_state_machine_yaml_minimal(yaml_text: str):
    # Minimal parser for our simple YAML structure (no external deps)
    # Extract terminal_states list and state names under "states:"
    terminal = []
    states = set()
    mode = None
    for raw in yaml_text.splitlines():
        line = raw.rstrip("\n")
        s = line.strip()
        if s.startswith("terminal_states:"):
            mode = "terminal"
            continue
        if s.startswith("states:"):
            mode = "states"
            continue
        if mode == "terminal":
            if s.startswith("- "):
                terminal.append(s[2:].strip())
            elif s and not s.startswith("#"):
                # end terminal section if other keys appear
                pass
        if mode == "states":
            # state key lines look like "PENDING:" at indent 2
            if raw.startswith("  ") and not raw.startswith("    ") and s.endswith(":") and not s.startswith("#"):
                st = s[:-1].strip()
                if st:
                    states.add(st)
    return terminal, states

def add_check(checks, status, name, message, details=None, err_code=""):
    checks.append({
        "status": status,
        "name": name,
        "message": message,
        "details": details or {},
        "err_code": err_code
    })

def main():
    os.makedirs(OUTBOX, exist_ok=True)
    checks = []

    # 1) Existence
    for p in [INV_PATH, ERR_PATH, SM_PATH, STRUCT_VERIFIER]:
        if not os.path.exists(p):
            add_check(checks, "FAIL", "FILE_EXISTS", f"Missing required file: {p}", err_code="ERR-OPS-003")
            overall = "FAIL"
            write_report(checks, overall)
            return

    inv_md = read_text(INV_PATH)
    err_md = read_text(ERR_PATH)
    sm_txt = read_text(SM_PATH)

    inv_ids = parse_invariant_ids(inv_md)
    err_codes = parse_err_codes(err_md)
    terminal, sm_states = parse_state_machine_yaml_minimal(sm_txt)

    # 2) Dictionary sanity
    required_invariants = {"INV-STRUCT-001","INV-STRUCT-002","INV-STRUCT-003","INV-STRUCT-004","INV-CRYPTO-001","INV-CRYPTO-002","INV-OPS-001","INV-OPS-002"}
    missing_inv = sorted(list(required_invariants - inv_ids))
    if missing_inv:
        add_check(checks, "FAIL", "INV_CATALOG", "Missing required invariant IDs", {"missing": missing_inv}, err_code="ERR-OPS-003")
    else:
        add_check(checks, "PASS", "INV_CATALOG", "Required invariants present")

    required_err = {"ERR-STRUCT-001","ERR-STRUCT-002","ERR-STRUCT-003","ERR-STRUCT-004","ERR-OPS-003"}
    missing_err = sorted(list(required_err - err_codes))
    if missing_err:
        add_check(checks, "FAIL", "ERR_CATALOG", "Missing required ERR codes", {"missing": missing_err}, err_code="ERR-OPS-003")
    else:
        add_check(checks, "PASS", "ERR_CATALOG", "Required ERR codes present")

    if "OK" not in terminal or "QUARANTINED" not in terminal:
        add_check(checks, "FAIL", "STATE_MACHINE", "terminal_states must include OK and QUARANTINED", {"terminal_states": terminal}, err_code="ERR-OPS-003")
    else:
        add_check(checks, "PASS", "STATE_MACHINE", "terminal_states includes OK and QUARANTINED")

    if "RUNNING" not in sm_states or "GOVERNANCE_ACTION_REQUIRED" not in sm_states:
        add_check(checks, "FAIL", "STATE_MACHINE", "states must include RUNNING and GOVERNANCE_ACTION_REQUIRED", {"states": sorted(list(sm_states))}, err_code="ERR-OPS-003")
    else:
        add_check(checks, "PASS", "STATE_MACHINE", "states include RUNNING and GOVERNANCE_ACTION_REQUIRED")

    # 3) Execute STRUCT verifier (must PASS)
    try:
        r = subprocess.run(["python", STRUCT_VERIFIER], capture_output=True, text=True)
        add_check(checks, "PASS" if r.returncode == 0 else "FAIL", "RUN_STRUCT_VERIFY", "Executed struct_verify_v1.py", {"stdout": r.stdout[-4000:], "stderr": r.stderr[-4000:]}, err_code="ERR-OPS-003" if r.returncode != 0 else "")
    except Exception as e:
        add_check(checks, "FAIL", "RUN_STRUCT_VERIFY", "Failed to execute struct verifier", {"error": str(e)}, err_code="ERR-OPS-003")

    if not os.path.exists(STRUCT_REPORT):
        add_check(checks, "FAIL", "STRUCT_REPORT", "struct report missing", {"path": STRUCT_REPORT}, err_code="ERR-OPS-003")
    else:
        try:
            with open(STRUCT_REPORT, "r", encoding="utf-8") as f:
                sr = json.load(f)
            overall_struct = sr.get("results", {}).get("overall", "FAIL")
            if overall_struct == "PASS":
                add_check(checks, "PASS", "STRUCT_REPORT", "struct report PASS")
            else:
                add_check(checks, "FAIL", "STRUCT_REPORT", "struct report not PASS", {"overall": overall_struct, "checks": sr.get("results", {}).get("checks", [])}, err_code="ERR-STRUCT-002")
        except Exception as e:
            add_check(checks, "FAIL", "STRUCT_REPORT", "Failed to parse struct report", {"error": str(e)}, err_code="ERR-OPS-003")

    # 4) Overall
    overall = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    write_report(checks, overall)

def write_report(checks, overall):
    report = {
        "report_version": "v1",
        "utc_now": utc_now(),
        "verifier": {"name": "final_check_dict_driven", "version": "v1"},
        "inputs": {"base": BASE},
        "results": {"overall": overall, "checks": checks},
    }
    os.makedirs(OUTBOX, exist_ok=True)
    with open(OUT_REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print("Wrote report:", OUT_REPORT)
    print("Overall:", overall)

if __name__ == "__main__":
    main()