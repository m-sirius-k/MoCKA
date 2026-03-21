import subprocess
import sys
from datetime import datetime, UTC

LOG_FILE = "observer_audit.log"

def log(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now(UTC).isoformat()} | {msg}\n")

def run_logged(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        log("ERROR running: " + " ".join(cmd))
        log(p.stdout.strip())
        log(p.stderr.strip())
        print("ERROR")
        sys.exit(p.returncode)
    log("OK: " + " ".join(cmd))
    return p.stdout.strip()

def run_silent(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        print("ERROR")
        sys.exit(p.returncode)
    return p.stdout.strip()

if __name__ == "__main__":
    # 1) 監査対象（verify結果）を audit.log に固定化
    run_logged([sys.executable, "verify_chain.py"])
    run_logged([sys.executable, "transition_verify.py"])
    log("OBSERVER_OK")

    # 2) audit.log を封印（封印処理自体は audit.log に書かない）
    run_silent([sys.executable, "observer_seal.py"])

    print("OBSERVER_OK")
