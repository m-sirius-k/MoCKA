"""
anchor_update.py
変更をコミット後にanchor_recordを自動更新して再封印する
使い方: python anchor_update.py "コミットメッセージ"
"""
import subprocess
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"C:\Users\sirok\MoCKA")
ANCHOR_PATHS = [
    ROOT / "governance" / "anchor_record.json",
    ROOT / "mocka-governance-kernel" / "anchors" / "anchor_record.json",
]
CALC_SCRIPT = ROOT / "governance" / "calc_summary_hash.py"

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout.strip(), r.returncode

def get_summary_hash(commit):
    # anchor_recordを一時的に新コミットで更新してハッシュ計算
    for p in ANCHOR_PATHS:
        ar = json.loads(p.read_text(encoding="utf-8"))
        ar["external_ref"] = f"https://github.com/m-sirius-k/MoCKA/commit/{commit}"
        ar["sealed_summary_hash"] = "0" * 64  # 仮値
        p.write_text(json.dumps(ar, indent=2, ensure_ascii=False), encoding="utf-8")

    out, _ = run([sys.executable, str(CALC_SCRIPT)])
    for line in out.splitlines():
        if line.startswith("sealed_summary_hash:"):
            return line.split(": ", 1)[1].strip()
    return None

def main():
    msg = sys.argv[1] if len(sys.argv) > 1 else "update: auto anchor update"

    # 1. 変更をコミット
    run(["git", "add", "-A"])
    run(["git", "commit", "-m", msg])
    commit, _ = run(["git", "log", "--format=%H", "-1"])
    print(f"COMMIT: {commit}")

    # 2. summary_hash計算
    summary_hash = get_summary_hash(commit)
    if not summary_hash:
        print("ERROR: failed to calculate summary_hash")
        sys.exit(1)
    print(f"SUMMARY_HASH: {summary_hash}")

    # 3. anchor_record更新
    for p in ANCHOR_PATHS:
        ar = json.loads(p.read_text(encoding="utf-8"))
        ar["sealed_summary_hash"] = summary_hash
        ar["external_ref"] = f"https://github.com/m-sirius-k/MoCKA/commit/{commit}"
        ar["sealed_at_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        p.write_text(json.dumps(ar, indent=2, ensure_ascii=False), encoding="utf-8")

    # 4. anchor_record自体をコミット
    run(["git", "add", "-A"])
    run(["git", "commit", "-m", f"anchor: re-seal after {commit[:7]}"])
    print("ANCHOR UPDATED AND COMMITTED")

    # 5. 検証
    out, code = run([sys.executable, str(ROOT / "verify_all.py")])
    print(out)
    return code

if __name__ == "__main__":
    sys.exit(main())
