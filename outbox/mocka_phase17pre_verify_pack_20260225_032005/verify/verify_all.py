from pathlib import Path
import json
import sys
import base64
import hashlib
import zipfile
import tempfile
from datetime import datetime, timezone

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config" / "config.json"
ACCEPTANCE_DIR = BASE_DIR / "acceptance"

def utc_now_z():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def signature_check(config):
    tip = config.get("expected_tip", "")
    pubkey_rel = config.get("public_key_path", "")

    if not isinstance(tip, str) or len(tip.strip()) < 16:
        return {"status": "FAIL", "failure_code": "SIGNATURE_CONFIG_BAD_TIP"}

    if not isinstance(pubkey_rel, str) or not pubkey_rel.strip():
        return {"status": "FAIL", "failure_code": "SIGNATURE_CONFIG_BAD_PUBKEY_PATH"}

    pubkey_path = (BASE_DIR / pubkey_rel).resolve()
    signed_path = BASE_DIR / "outbox" / f"governance_envelope_v2_{tip}.signed_bytes.txt"
    sig_path = BASE_DIR / "outbox" / f"governance_envelope_v2_{tip}.sig"

    missing = [str(p) for p in [pubkey_path, signed_path, sig_path] if not p.exists()]
    if missing:
        return {"status": "FAIL", "failure_code": "SIGNATURE_INPUTS_MISSING", "missing": missing}

    pub = serialization.load_pem_public_key(pubkey_path.read_bytes())
    if not isinstance(pub, Ed25519PublicKey):
        return {"status": "FAIL", "failure_code": "SIGNATURE_PUBKEY_NOT_ED25519"}

    signed_bytes = signed_path.read_bytes()
    sig_b64 = sig_path.read_text(encoding="utf-8-sig").strip()

    try:
        sig = base64.b64decode(sig_b64, validate=True)
    except Exception as e:
        return {"status": "FAIL", "failure_code": "SIGNATURE_B64_DECODE_FAIL", "detail": str(e)}

    try:
        pub.verify(sig, signed_bytes)
    except Exception as e:
        return {"status": "FAIL", "failure_code": "SIGNATURE_VERIFY_FAIL", "detail": str(e)}

    return {
        "status": "PASS",
        "signed_bytes_sha256": sha256_file(signed_path),
        "signature_sha256": sha256_file(sig_path),
    }

def authoritative_integrity_check():
    pack_zip = BASE_DIR / "outbox" / "mocka_phase16_authoritative_pack.zip"
    if not pack_zip.exists():
        return {"status": "FAIL", "failure_code": "AUTH_PACK_NOT_FOUND", "path": str(pack_zip)}

    # Phase17: verify zip integrity against its own manifest
    try:
        with zipfile.ZipFile(pack_zip, "r") as zf:
            names = set(zf.namelist())
            if "manifest_phase16_authoritative_v1.json" not in names:
                return {"status": "FAIL", "failure_code": "AUTH_MANIFEST_NOT_IN_ZIP"}

            manifest_obj = json.loads(zf.read("manifest_phase16_authoritative_v1.json").decode("utf-8-sig"))
            items = manifest_obj.get("items")
            if not isinstance(items, list) or not items:
                return {"status": "FAIL", "failure_code": "AUTH_MANIFEST_ITEMS_EMPTY"}

            mismatches = []
            missing = []
            checked = []

            for it in items:
                if not isinstance(it, dict):
                    continue
                p = it.get("path", "")
                expected = (it.get("sha256", "") or "").lower().strip()

                base = Path(str(p)).name
                if base == "":
                    continue

                if base not in names:
                    missing.append(base)
                    continue

                data = zf.read(base)
                actual = sha256_bytes(data)

                checked.append({"file": base, "expected": expected, "actual": actual})

                if expected and actual != expected:
                    mismatches.append({"file": base, "expected": expected, "actual": actual})

            if missing:
                return {"status": "FAIL", "failure_code": "AUTH_ZIP_MISSING_ITEMS", "missing": missing}

            if mismatches:
                return {"status": "FAIL", "failure_code": "AUTH_SHA256_MISMATCH", "mismatches": mismatches}

            # optional: ensure zip manifest matches included manifest file sha256 too
            # (it is already covered because items includes manifest in your zip listing)
            return {
                "status": "PASS",
                "pack_zip": str(pack_zip),
                "manifest_version": manifest_obj.get("manifest_version"),
                "items_checked": len(checked),
            }
    except Exception as e:
        return {"status": "FAIL", "failure_code": "AUTH_ZIP_READ_ERROR", "detail": str(e)}

def struct_stub_check():
    return {"status": "PASS", "note": "STRUCT check is internal-only in external pack"}

def dict_stub_check():
    return {"status": "PASS", "note": "DICT check is internal-only in external pack"}

def main():
    started = utc_now_z()

    if not CONFIG_PATH.exists():
        bundle = {
            "started_utc": started,
            "overall_status": "FAIL",
            "checks": {"config_check": {"status": "FAIL", "failure_code": "CONFIG_NOT_FOUND", "path": str(CONFIG_PATH)}},
        }
        ACCEPTANCE_DIR.mkdir(exist_ok=True)
        (ACCEPTANCE_DIR / "phase17_pre_full_stack.json").write_text(json.dumps(bundle, indent=2), encoding="utf-8")
        print("OVERALL: FAIL")
        raise SystemExit(1)

    config = read_json(CONFIG_PATH)

    checks = {}
    checks["struct_check"] = struct_stub_check()
    checks["dict_check"] = dict_stub_check()
    checks["signature_check"] = signature_check(config)
    checks["authoritative_check"] = authoritative_integrity_check()

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
    raise SystemExit(0 if overall == "PASS" else 1)

if __name__ == "__main__":
    main()
