import json
from pathlib import Path
from base64 import b64encode
from cryptography.hazmat.primitives import serialization

from canonical import canonical_bytes, canonical_loads, read_bytes

BASE = Path(__file__).resolve().parent
KEYS = BASE / "keys"
SAMPLES = BASE / "samples"

def load_priv(path: Path):
    return serialization.load_pem_private_key(path.read_bytes(), password=None)

def main():
    target = SAMPLES / "valid_2_of_3.json"
    event = canonical_loads(read_bytes(target))

    # 署名対象は signatures を除いた本体
    unsigned = dict(event)
    unsigned.pop("signatures", None)

    msg = canonical_bytes(unsigned)

    signers = [
        ("authority_b_v1", KEYS / "authority_b_private.pem"),
        ("authority_c_v1", KEYS / "authority_c_private.pem"),
    ]

    sigs = []
    for key_id, priv_path in signers:
        priv = load_priv(priv_path)
        sig = priv.sign(msg)
        sigs.append({
            "key_id": key_id,
            "signature_b64": b64encode(sig).decode("ascii")
        })

    event["signatures"] = sigs

    # canonicalで上書き
    target.write_bytes(canonical_bytes(event) + b"\n")

    print("OK: valid_2_of_3.json re-signed by authority_b_v1 + authority_c_v1")

if __name__ == "__main__":
    main()