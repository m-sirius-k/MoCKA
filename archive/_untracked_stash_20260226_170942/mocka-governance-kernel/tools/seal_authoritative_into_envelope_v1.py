# file: C:\Users\sirok\MoCKA\mocka-governance-kernel\tools\seal_authoritative_into_envelope_v1.py
# Phase16: seal authoritative report into a new envelope and sign it
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Tuple, Optional

FAIL="FAIL"; PASS="PASS"

def utc() -> str:
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

def read_json(path: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    b, e = read_bytes(path)
    if e:
        return None, e
    try:
        return json.loads(b.decode("utf-8")), None
    except UnicodeDecodeError:
        return None, "UTF8_DECODE_ERROR"
    except json.JSONDecodeError:
        return None, "JSON_PARSE_ERROR"

def write_json(path: str, obj: Dict[str, Any]) -> Optional[str]:
    try:
        d = os.path.dirname(path)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=True, indent=2, sort_keys=True)
        return None
    except OSError:
        return "FILE_WRITE_ERROR"

def write_text(path: str, text: str) -> Optional[str]:
    try:
        d = os.path.dirname(path)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        return None
    except OSError:
        return "FILE_WRITE_ERROR"

def load_private_key_ed25519(pem_bytes: bytes):
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    except Exception:
        return None, "CRYPTOGRAPHY_IMPORT_ERROR"
    try:
        k = serialization.load_pem_private_key(pem_bytes, password=None)
    except ValueError:
        return None, "PRIVATE_KEY_PEM_PARSE_ERROR"
    except Exception:
        return None, "PRIVATE_KEY_LOAD_ERROR"
    if not isinstance(k, Ed25519PrivateKey):
        return None, "PRIVATE_KEY_WRONG_TYPE"
    return k, None

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--authoritative-report", required=True)
    ap.add_argument("--tip-hash", required=True)
    ap.add_argument("--private-key", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--prefix", default="governance_envelope_v2a")
    a = ap.parse_args()

    rep_path = os.path.abspath(a.authoritative_report)
    tip = a.tip_hash.strip()
    key_path = os.path.abspath(a.private_key)
    out_dir = os.path.abspath(a.out_dir)

    rep_obj, err = read_json(rep_path)
    if err:
        return 10

    rep_bytes = json.dumps(rep_obj, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    rep_sha = sha256_hex(rep_bytes)

    envelope = {
        "schema": "mocka.governance.envelope",
        "envelope_version": "v2a",
        "created_at_utc": utc(),
        "tip_hash": tip,
        "payload": {
            "type": "authoritative_report_v1",
            "sha256": rep_sha,
            "path_hint": rep_path,
            "body": rep_obj
        }
    }

    signed_bytes = json.dumps(envelope, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")

    key_pem, err = read_bytes(key_path)
    if err:
        return 11
    priv, err = load_private_key_ed25519(key_pem)
    if err:
        return 12

    sig_raw = priv.sign(signed_bytes)
    sig_b64 = base64.b64encode(sig_raw).decode("ascii")

    base = f"{a.prefix}_{tip}"
    out_env = os.path.join(out_dir, base + ".json")
    out_sb  = os.path.join(out_dir, base + ".signed_bytes.txt")
    out_sig = os.path.join(out_dir, base + ".sig")

    e = write_json(out_env, envelope)
    if e:
        return 20
    e = write_text(out_sb, signed_bytes.decode("utf-8"))
    if e:
        return 21
    e = write_text(out_sig, sig_b64 + "\n")
    if e:
        return 22

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
