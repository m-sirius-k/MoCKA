import subprocess, sys, hashlib
from pathlib import Path
import json, re

ANCHOR_PATH = Path("mocka-governance-kernel/anchors/anchor_record.json")
EXCLUDE_PATHS = {"mocka-governance-kernel/anchors/anchor_record.json"}

def run_text(cmd):
    r = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace")
    return r.stdout

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def extract_commit(external_ref):
    m = re.search(r"/commit/([0-9a-fA-F]{7,40})", external_ref)
    if not m:
        raise SystemExit("ERROR: external_ref must contain /commit/<hash>")
    return m.group(1).lower()

def main():
    ar = json.loads(ANCHOR_PATH.read_text(encoding="utf-8-sig"))
    sealing_commit = extract_commit(ar.get("external_ref", ""))

    # git ls-tree -r でblob一覧を取得（git showなし）
    r = subprocess.run(
        ["git", "ls-tree", "-r", sealing_commit],
        capture_output=True
    )
    lines = r.stdout

    # EXCLUDE適用
    filtered = []
    for line in lines.splitlines():
        parts = line.split(b"\t", 1)
        if len(parts) == 2:
            path = parts[1].decode("utf-8", errors="replace").replace("\\", "/")
            if path not in EXCLUDE_PATHS:
                filtered.append(line)

    combined = b"\n".join(filtered)
    summary_hash = sha256_hex(combined)
    print(f"sealed_summary_hash: {summary_hash}")
    return 0

if __name__ == "__main__":
    sys.exit(main())