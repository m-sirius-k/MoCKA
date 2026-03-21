from pathlib import Path
import json
import sys
import subprocess
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config" / "config.json"
ACCEPTANCE_DIR = BASE_DIR / "acceptance"
GOV_DB_PATH = BASE_DIR / "mocka-governance-kernel" / "governance" / "governance.db"

DICT_SCRIPT = BASE_DIR / "governance_phase16_upgrade" / "final_check_dict_driven_v1.py"
DICT_REPORT = BASE_DIR / "outbox" / "verify_report_final_check_v1.json"

SIG_SCRIPT = BASE_DIR / "mocka-governance-kernel" / "tools" / "verify_envelope_v2_signature_v1.py"
SIG_REPORT = BASE_DIR / "outbox" / "verify_report_signature_v1.json"

AUTH_SCRIPT = BASE_DIR / "mocka-governance-kernel" / "tools" / "final_check_authoritative_v1.py"
AUTH_REPORT = BASE_DIR / "outbox" / "verify_report_authoritative_v1.json"

def utc_now_z():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError("config.json not found")
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8-sig"))

def struct_check():
    if not GOV_DB_PATH.exists():
        return {"status": "FAIL", "failure_code": "STRUCT_DB_NOT_FOUND"}
    return {"status": "PASS"}

def _run(argv, timeout_sec):
    try:
        cp = subprocess.run(
            argv,
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=timeout_sec,
        )
    except Exception as e:
        return None, {"status": "FAIL", "failure_code": "SCRIPT_EXEC_ERROR", "detail": str(e)}

    if cp.returncode != 0:
        return None, {
            "status": "FAIL",
            "failure_code": "SCRIPT_NONZERO_EXIT",
            "returncode": cp.returncode,
            "stderr_tail": (cp.stderr or "")[-2000:],
        }

    return cp, None

def dict_check():
    _, err = _run([sys.executable, str(DICT_SCRIPT)], 180)
    if err:
        return err
    report = json.loads(DICT_REPORT.read_text(encoding="utf-8-sig"))
    overall = report.get("results", {}).get("overall")
    return {"status": "PASS"} if overall == "PASS" else {"status": "FAIL"}

def signature_check(config):
    tip = config["expected_tip"]
    pubkey = BASE_DIR / config["public_key_path"]
    signed = BASE_DIR / "outbox" / f"governance_envelope_v2_{tip}.signed_bytes.txt"
    sig = BASE_DIR / "outbox" / f"governance_envelope_v2_{tip}.sig"

    argv = [
        sys.executable,
        str(SIG_SCRIPT),
        "--signed-bytes", str(signed),
        "--signature", str(sig),
        "--public-key", str(pubkey),
        "--out-report", str(SIG_REPORT),
        "--sig-format", "b64",
    ]

    _, err = _run(argv, 180)
    if err:
        return err

    report = json.loads(SIG_REPORT.read_text(encoding="utf-8-sig"))
    return {"status": "PASS"} if report.get("status") == "PASS" else {"status": "FAIL"}

def authoritative_check():
    _, err = _run([sys.executable, str(AUTH_SCRIPT)], 180)
    if err:
        return err

    if not AUTH_REPORT.exists():
        return {"status": "FAIL", "failure_code": "AUTH_REPORT_NOT_FOUND"}

    report = json.loads(AUTH_REPORT.read_text(encoding="utf-8-sig"))
    overall = report.get("overall") or report.get("status")
    return {"status": "PASS"} if overall == "PASS" else {"status": "FAIL"}

def main():
    started = utc_now_z()
    config = load_config()

    checks = {
        "struct_check": struct_check(),
        "dict_check": dict_check(),
        "signature_check": signature_check(config),
        "authoritative_check": authoritative_check(),
    }

    overall = "PASS"
    for v in checks.values():
        if v.get("status") != "PASS":
            overall = "FAIL"

    bundle = {
        "started_utc": started,
        "overall_status": overall,
        "checks": checks,
    }

    ACCEPTANCE_DIR.mkdir(exist_ok=True)
    out = ACCEPTANCE_DIR / "phase17_pre_full_stack.json"
    out.write_text(json.dumps(bundle, indent=2), encoding="utf-8")

    print("OVERALL:", overall)
    sys.exit(0 if overall == "PASS" else 1)

if __name__ == "__main__":
    main()
