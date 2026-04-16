# file: C:\Users\sirok\MoCKA\mocka-governance-kernel\tools\verify_envelope_v2_signature_v1.py
# NOTE: Phase16 Envelope v2 signature verification (ed25519)
# NOTE: Policy: no uncaught exceptions, classified failure_code, always emits JSON report
from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import os
import traceback
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

FAIL = "FAIL"
PASS = "PASS"

def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def read_bytes(path: str) -> Tuple[Optional[bytes], Optional[str]]:
    try:
        with open(path, "rb") as f:
            return f.read(), None
    except FileNotFoundError:
        return None, "FILE_NOT_FOUND"
    except PermissionError:
        return None, "FILE_PERMISSION_DENIED"
    except OSError:
        return None, "FILE_READ_ERROR"

def write_report(path: str, obj: Dict[str, Any]) -> Optional[str]:
    try:
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=True, indent=2, sort_keys=True)
        return None
    except OSError:
        return "REPORT_WRITE_ERROR"

def decode_signature(sig_file_bytes: bytes, sig_format: str) -> Tuple[Optional[bytes], Optional[str]]:
    fmt = (sig_format or "").strip().lower()

    if fmt == "raw":
        if len(sig_file_bytes) != 64:
            return None, "SIGNATURE_RAW_LENGTH_INVALID"
        return sig_file_bytes, None

    if fmt == "hex":
        try:
            s = sig_file_bytes.decode("ascii").strip()
            out = binascii.unhexlify(s)
        except Exception:
            return None, "SIGNATURE_HEX_DECODE_ERROR"
        if len(out) != 64:
            return None, "SIGNATURE_LENGTH_INVALID"
        return out, None

    if fmt in ("b64", "base64"):
        try:
            s = sig_file_bytes.decode("ascii").strip()
            out = base64.b64decode(s, validate=True)
        except Exception:
            return None, "SIGNATURE_B64_DECODE_ERROR"
        if len(out) != 64:
            return None, "SIGNATURE_LENGTH_INVALID"
        return out, None

    return None, "SIGNATURE_FORMAT_UNSUPPORTED"

def load_ed25519_public_key(pem_bytes: bytes) -> Tuple[Optional[Any], Optional[str]]:
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except Exception:
        return None, "CRYPTOGRAPHY_IMPORT_ERROR"

    try:
        key = serialization.load_pem_public_key(pem_bytes)
    except ValueError:
        return None, "PUBLIC_KEY_PEM_PARSE_ERROR"
    except Exception:
        return None, "PUBLIC_KEY_LOAD_ERROR"

    if not isinstance(key, Ed25519PublicKey):
        return None, "PUBLIC_KEY_WRONG_TYPE"

    return key, None

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--signed-bytes", required=True)
    ap.add_argument("--signature", required=True)
    ap.add_argument("--public-key", required=True)
    ap.add_argument("--out-report", required=True)
    ap.add_argument("--sig-format", default="raw", choices=["raw", "hex", "b64", "base64"])
    a = ap.parse_args()

    sb_path = os.path.abspath(a.signed_bytes)
    sig_path = os.path.abspath(a.signature)
    pk_path = os.path.abspath(a.public_key)
    out_path = os.path.abspath(a.out_report)

    report: Dict[str, Any] = {
        "report_version": "signature_check_v1",
        "generated_at_utc": utc_now(),
        "status": FAIL,
        "failure_code": None,
        "signature_check": {
            "signed_bytes_path": sb_path,
            "signature_path": sig_path,
            "public_key_path": pk_path,
            "signature_format": a.sig_format,
            "public_key_fingerprint_sha256": None,
            "signed_bytes_sha256": None,
            "signature_file_sha256": None,
            "signature_valid": False,
        },
    }

    try:
        signed_bytes, err = read_bytes(sb_path)
        if err is not None:
            report["failure_code"] = f"SIGNED_BYTES_{err}"
            write_report(out_path, report)
            return 10
        report["signature_check"]["signed_bytes_sha256"] = sha256_hex(signed_bytes)

        sig_file_bytes, err = read_bytes(sig_path)
        if err is not None:
            report["failure_code"] = f"SIGNATURE_{err}"
            write_report(out_path, report)
            return 11
        report["signature_check"]["signature_file_sha256"] = sha256_hex(sig_file_bytes)

        signature, err = decode_signature(sig_file_bytes, a.sig_format)
        if err is not None:
            report["failure_code"] = err
            write_report(out_path, report)
            return 12

        pub_pem, err = read_bytes(pk_path)
        if err is not None:
            report["failure_code"] = f"PUBLIC_KEY_{err}"
            write_report(out_path, report)
            return 13
        report["signature_check"]["public_key_fingerprint_sha256"] = sha256_hex(pub_pem)

        pubkey, err = load_ed25519_public_key(pub_pem)
        if err is not None:
            report["failure_code"] = err
            write_report(out_path, report)
            return 14

        try:
            pubkey.verify(signature, signed_bytes)
            report["signature_check"]["signature_valid"] = True
            report["status"] = PASS
            report["failure_code"] = None
        except Exception:
            report["signature_check"]["signature_valid"] = False
            report["status"] = FAIL
            report["failure_code"] = "SIGNATURE_INVALID"
            write_report(out_path, report)
            return 15

        werr = write_report(out_path, report)
        if werr is not None:
            report["status"] = FAIL
            report["failure_code"] = werr
            write_report(out_path, report)
            return 16

        return 0

    except Exception as ex:
        report["status"] = FAIL
        report["failure_code"] = "INTERNAL_ERROR"
        report["internal_error"] = {
            "type": type(ex).__name__,
            "message": str(ex),
            "traceback": traceback.format_exc(),
        }
        write_report(out_path, report)
        return 99

if __name__ == "__main__":
    raise SystemExit(main())
