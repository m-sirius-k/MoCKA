import os
import json

ROOT = r"C:\Users\sirok\MoCKA"
REGISTRY_PATH = os.path.join(ROOT, "audit", "key_registry.json")
PRIVATE_DIR = os.path.join(ROOT, "audit", "private")


def load_registry() -> dict:
    with open(REGISTRY_PATH, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def get_active_key_id() -> str:
    reg = load_registry()
    kid = reg.get("active_key_id")
    if not kid:
        raise RuntimeError("active_key_id missing in key_registry.json")
    return kid


def get_active_private_key_path() -> str:
    kid = get_active_key_id()
    p = os.path.join(PRIVATE_DIR, f"{kid}_private.pem")
    if not os.path.exists(p):
        raise FileNotFoundError(f"active private key missing: {p}")
    return p