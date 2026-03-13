import json
from pathlib import Path
from copy import deepcopy

from canonical import canonical_loads, read_bytes, canonical_bytes
from cryptography.hazmat.primitives import serialization
from base64 import b64encode

BASE = Path(__file__).resolve().parent
SAMPLES = BASE / "samples"
KEYS = BASE / "keys"

def load_priv(path: Path):
    return serialization.load_pem_private_key(path.read_bytes(), password=None)

def canonical_write(path: Path, obj: dict) -> None:
    path.write_bytes(canonical_bytes(obj) + b"\n")

def sign_event(unsigned_event: dict, signers: list[tuple[str, Path]]) -> list[dict]:
    msg = canonical_bytes(unsigned_event)
    sigs = []
    for key_id, priv_path in signers:
        priv = load_priv(priv_path)
        sig = priv.sign(msg)
        sigs.append({"key_id": key_id, "signature_b64": b64encode(sig).decode("ascii")})
    return sigs

def main():
    base_valid = canonical_loads(read_bytes(SAMPLES / "valid_2_of_3.json"))

    # unsigned base (no signatures)
    unsigned = dict(base_valid)
    unsigned.pop("signatures", None)

    # 1) insufficient_signature: b だけで署名（足りない）
    insufficient = deepcopy(unsigned)
    insufficient["signatures"] = sign_event(unsigned, [("authority_b_v1", KEYS / "authority_b_private.pem")])
    canonical_write(SAMPLES / "insufficient_signature.json", insufficient)

    # 2) duplicate_signer: b を2回（重複検出）
    duplicate = deepcopy(unsigned)
    duplicate["signatures"] = sign_event(unsigned, [
        ("authority_b_v1", KEYS / "authority_b_private.pem"),
        ("authority_b_v1", KEYS / "authority_b_private.pem"),
    ])
    canonical_write(SAMPLES / "duplicate_signer.json", duplicate)

    # 3) revoked_key_used: revoke済み a + b（revoke検出）
    revoked = deepcopy(unsigned)
    revoked["signatures"] = sign_event(unsigned, [
        ("authority_a_v1", KEYS / "authority_a_private.pem"),
        ("authority_b_v1", KEYS / "authority_b_private.pem"),
    ])
    canonical_write(SAMPLES / "revoked_key_used.json", revoked)

    # 4) canonical_tamper: 正しい署名(b+c)を付けた後にpayloadを改変（署名不一致）
    tamper = deepcopy(unsigned)
    tamper["signatures"] = sign_event(unsigned, [
        ("authority_b_v1", KEYS / "authority_b_private.pem"),
        ("authority_c_v1", KEYS / "authority_c_private.pem"),
    ])
    # 署名後に1バイト変える
    tamper["payload"]["value"] = 999
    canonical_write(SAMPLES / "canonical_tamper.json", tamper)

    print("OK: fail samples regenerated (post-revoke aligned)")

if __name__ == "__main__":
    main()