from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict
from hashlib import sha256

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization


ROOT = Path(__file__).resolve().parents[1]


def canonical_json_bytes(obj: Any) -> bytes:
    s = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return s.encode("utf-8")


def load_private_key(priv_path: Path) -> Ed25519PrivateKey:
    data = priv_path.read_bytes()
    sk = serialization.load_pem_private_key(data, password=None)
    if not isinstance(sk, Ed25519PrivateKey):
        raise TypeError("private key is not Ed25519")
    return sk


def atomic_write_text(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_path", required=True)
    ap.add_argument("--out", dest="out_path", required=True)
    ap.add_argument("--key-id", dest="key_id", required=True)
    args = ap.parse_args()

    in_path = Path(args.in_path)
    out_path = Path(args.out_path)
    key_id = args.key_id.strip()

    priv_path = ROOT / "keys" / "private" / f"ed25519_{key_id}.pem"
    if not priv_path.exists():
        raise FileNotFoundError(f"missing private key: {priv_path}")

    sk = load_private_key(priv_path)

    wrapper = json.loads(in_path.read_text(encoding="utf-8"))

    if wrapper.get("schema") != "mocka.pack.wrapper.signed.v2":
        raise ValueError(f"unsupported schema: {wrapper.get('schema')}")

    rows = wrapper.get("rows")
    if not isinstance(rows, list):
        raise ValueError("wrapper.rows must be list")

    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"row[{i}] must be object")

        row_to_sign = dict(row)
        row_to_sign.pop("row_sig", None)
        row_to_sign.pop("row_sig_alg", None)
        row_to_sign.pop("key_id", None)

        msg = canonical_json_bytes(row_to_sign)
        sig = sk.sign(msg)

        row["row_sig"] = sig.hex()
        row["row_sig_alg"] = "ed25519"
        row["key_id"] = key_id

    out_text = json.dumps(wrapper, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    atomic_write_text(out_path, out_text)

    print("OK")
    print(f"in ={in_path}")
    print(f"out={out_path}")
    print(f"key_id={key_id}")
    print(f"rows_signed={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())