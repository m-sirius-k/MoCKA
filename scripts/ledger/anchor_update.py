import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿"""
anchor_update.py
変更をコミット後にanchor_recordを自動更新して再封印する
使い方: python anchor_update.py "コミットメッセージ"
"""
import subprocess
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

PRE_COMMIT_FORBIDDEN = [
    "TestProfile/",
    "Default/Cache/",
    "chrome_debug/",
    ".env",
    "secrets/",
]

def check_staged_files():
    """git add済みファイルに禁止パターンが含まれていないか確認"""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True, cwd=ROOT
    )
    staged = result.stdout.splitlines()
    violations = []
    for f in staged:
        for forbidden in PRE_COMMIT_FORBIDDEN:
            if forbidden.lower() in f.lower():
                violations.append(f)
    if violations:
        print(f"[SEAL BLOCKED] forbidden pattern detected: {violations}")
        print("Run 'git rm --cached <file>' to exclude it, then retry.")
        sys.exit(1)
    print(f"[SEAL OK] staged {len(staged)} file(s), no forbidden patterns")

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace")
    return r.stdout.strip(), r.returncode

def get_summary_hash(commit):
    for p in ANCHOR_PATHS:
        ar = json.loads(p.read_text(encoding="utf-8"))
        ar["external_ref"] = f"https://github.com/m-sirius-k/MoCKA/commit/{commit}"
        ar["sealed_summary_hash"] = "0" * 64
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
    check_staged_files()
    out, code = run(["git", "commit", "-m", msg])
    print(out if out else "nothing to commit")

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
