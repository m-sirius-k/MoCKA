# file: C:\Users\sirok\MoCKA\mocka-governance-kernel\tools\final_check_authoritative_v1.py
# Phase16 Authoritative Audit Report Generator
# STRUCT + DICT + SIGNATURE = AND (single PASS)
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Tuple, Optional

FAIL = "FAIL"
PASS = "PASS"

def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def read_json(path: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, "FILE_NOT_FOUND"
    except PermissionError:
        return None, "FILE_PERMISSION_DENIED"
    except OSError:
        return None, "FILE_READ_ERROR"
    except json.JSONDecodeError:
        return None, "JSON_PARSE_ERROR"

def truthy(x: Any) -> bool:
    if x is None:
        return False
    if isinstance(x, bool):
        return x
    if isinstance(x, str):
        return x.strip() != ""
    if isinstance(x, (list, dict, tuple, set)):
        return len(x) > 0
    return True

def list_status_strings(obj: Any, out: list) -> None:
    # recursively collect strings like "PASS/FAIL/OK/NG" from keys that look like status fields
    if isinstance(obj, dict):
        for k, v in obj.items():
            lk = str(k).lower()
            if lk in ("status", "result", "verdict", "ok", "pass", "ng", "fail"):
                if isinstance(v, str):
                    out.append(v.strip())
                elif isinstance(v, bool):
                    out.append("PASS" if v else "FAIL")
            list_status_strings(v, out)
    elif isinstance(obj, list):
        for it in obj:
            list_status_strings(it, out)

def infer_pass_from_struct_or_dict(r: Dict[str, Any]) -> Tuple[bool, str]:
    # Rule:
    # - if fatal_error is truthy => FAIL
    # - else if any nested status-like string contains FAIL/NG/ERROR => FAIL
    # - else PASS
    if truthy(r.get("fatal_error")):
        return False, "FATAL_ERROR_PRESENT"

    statuses: list = []
    list_status_strings(r.get("results"), statuses)

    bad = []
    for s in statuses:
        u = s.upper()
        if "FAIL" in u or u == "NG" or "ERROR" in u:
            bad.append(s)

    if bad:
        return False, "RESULTS_CONTAIN_FAILURE"

    # If there were no status-like signals, still treat as PASS only if results exists (non-empty)
    if not truthy(r.get("results")):
        return False, "RESULTS_MISSING_OR_EMPTY"

    return True, "OK"

def infer_pass_signature(r: Dict[str, Any]) -> Tuple[bool, str]:
    if r.get("status") != "PASS":
        return False, "SIGNATURE_REPORT_STATUS_NOT_PASS"
    sc = r.get("signature_check", {})
    if sc.get("signature_valid") is not True:
        return False, "SIGNATURE_VALID_FALSE"
    return True, "OK"

def write_json(path: str, obj: Dict[str, Any]) -> Optional[str]:
    try:
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=True, indent=2, sort_keys=True)
        return None
    except OSError:
        return "REPORT_WRITE_ERROR"

def main() -> int:
    struct_path = r"C:\Users\sirok\MoCKA\outbox\verify_report_struct_v1.json"
    dict_path   = r"C:\Users\sirok\MoCKA\outbox\verify_report_final_check_v1.json"
    sig_path    = r"C:\Users\sirok\MoCKA\outbox\verify_report_signature_v1.json"
    out_path    = r"C:\Users\sirok\MoCKA\outbox\verify_report_authoritative_v1.json"

    report: Dict[str, Any] = {
        "report_version": "authoritative_v1",
        "generated_at_utc": utc(),
        "status": FAIL,
        "failure_code": None,
        "inputs": {
            "struct_report": struct_path,
            "dict_report": dict_path,
            "signature_report": sig_path
        },
        "checks": {
            "struct": {"pass": False, "reason": None},
            "dict": {"pass": False, "reason": None},
            "signature": {"pass": False, "reason": None}
        },
        "struct_check": None,
        "dict_check": None,
        "signature_check": None
    }

    struct, err = read_json(struct_path)
    if err:
        report["failure_code"] = "STRUCT_" + err
        write_json(out_path, report)
        return 10

    dict_r, err = read_json(dict_path)
    if err:
        report["failure_code"] = "DICT_" + err
        write_json(out_path, report)
        return 11

    sig, err = read_json(sig_path)
    if err:
        report["failure_code"] = "SIGNATURE_" + err
        write_json(out_path, report)
        return 12

    report["struct_check"] = struct
    report["dict_check"] = dict_r
    report["signature_check"] = sig

    s_ok, s_reason = infer_pass_from_struct_or_dict(struct)
    d_ok, d_reason = infer_pass_from_struct_or_dict(dict_r)
    g_ok, g_reason = infer_pass_signature(sig)

    report["checks"]["struct"]["pass"] = s_ok
    report["checks"]["struct"]["reason"] = s_reason
    report["checks"]["dict"]["pass"] = d_ok
    report["checks"]["dict"]["reason"] = d_reason
    report["checks"]["signature"]["pass"] = g_ok
    report["checks"]["signature"]["reason"] = g_reason

    if s_ok and d_ok and g_ok:
        report["status"] = PASS
        report["failure_code"] = None
    else:
        report["status"] = FAIL
        report["failure_code"] = "LOGICAL_AND_FAILED"

    write_json(out_path, report)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
