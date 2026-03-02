import json
from pathlib import Path
from copy import deepcopy

BASE = Path(__file__).resolve().parent
SAMPLES = BASE / "samples"

def canonical_text(obj: dict) -> str:
    return json.dumps(obj, separators=(",", ":"), sort_keys=True)

def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, obj: dict) -> None:
    path.write_text(canonical_text(obj) + "\n", encoding="utf-8")

def main():
    SAMPLES.mkdir(parents=True, exist_ok=True)

    base = load_json(SAMPLES / "valid_2_of_3.json")

    # 1) insufficient_signature: 署名が1つだけ
    insufficient = deepcopy(base)
    insufficient["signatures"] = insufficient["signatures"][:1]
    write_json(SAMPLES / "insufficient_signature.json", insufficient)

    # 2) duplicate_signer: 同じ署名者が2回登場
    duplicate = deepcopy(base)
    duplicate["signatures"][1]["key_id"] = duplicate["signatures"][0]["key_id"]
    write_json(SAMPLES / "duplicate_signer.json", duplicate)

    # 3) revoked_key_used: revoke済み想定のkey_idに差し替え
    revoked = deepcopy(base)
    revoked["signatures"][0]["key_id"] = "authority_a_revoked_v1"
    write_json(SAMPLES / "revoked_key_used.json", revoked)

    # 4) canonical_tamper: payloadを1文字でも変えると署名が死ぬ
    tamper = deepcopy(base)
    tamper["payload"]["value"] = 999
    write_json(SAMPLES / "canonical_tamper.json", tamper)

    print("OK: 4 fail samples created")
    print("OK: total 5 samples in ./samples")

if __name__ == "__main__":
    main()