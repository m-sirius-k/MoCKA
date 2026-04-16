# MoCKA File Protection Check
# mocka-checkから呼び出される

import hashlib, json, sys
from pathlib import Path

REGISTRY = Path(r"C:\Users\sirok\MoCKA\governance\file_protection_registry.json")

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""): h.update(chunk)
    return h.hexdigest()

def check():
    if not REGISTRY.exists():
        print("[PROTECTION] WARNING: registry not found")
        return
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    all_ok = True
    for path, info in reg["files"].items():
        expected = info["sha256"]
        try:
            actual = sha256(path)
            if actual == expected:
                print(f"[PROTECTION] OK: {Path(path).name}")
            else:
                print(f"[PROTECTION] !! MODIFIED: {Path(path).name}")
                print(f"  expected: {expected[:16]}...")
                print(f"  actual  : {actual[:16]}...")
                all_ok = False
        except FileNotFoundError:
            print(f"[PROTECTION] !! MISSING: {Path(path).name}")
            all_ok = False
    if all_ok:
        print("[PROTECTION] ALL PROTECTED FILES INTACT")
    else:
        print("[PROTECTION] WARNING: MODIFIED FILES DETECTED - confirm with きむら博士")

check()
