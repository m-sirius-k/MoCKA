"""
run_experiment.py
候補4(現状=ロックなし)のベースライン挙動と、候補1(ファイルロック)導入後の
挙動を、実際に複数プロセスを同時起動して比較計測する。
対象は PlanningCaliber/lock_verification/sandbox_repo のみ。本番リポジトリ・
本番events.dbには一切アクセスしない。
"""
import subprocess
import sys
import time
import json
import os
from pathlib import Path

ROOT = Path(r"C:\Users\sirok\MoCKA\PlanningCaliber\lock_verification\sandbox_repo")
HARNESS = Path(r"C:\Users\sirok\MoCKA\PlanningCaliber\lock_verification\sandbox_commit_harness.py")
LOCK_FILE = ROOT.parent / ".sandbox_git.lock"  # 修正: 作業ツリー外に配置(git add -Aに巻き込まれるバグを回避)
N_TRIALS = int(sys.argv[1]) if len(sys.argv) > 1 else 100
N_WORKERS = int(sys.argv[2]) if len(sys.argv) > 2 else 3
USE_LOCK = sys.argv[3] == "1" if len(sys.argv) > 3 else False


def reset_trial_state(trial_no):
    (ROOT / "dummy.txt").write_text(f"trial {trial_no} {time.time()}\n", encoding="utf-8")


def run_trial(trial_no):
    reset_trial_state(trial_no)
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()
    procs = []
    for w in range(N_WORKERS):
        args = [sys.executable, str(HARNESS), str(ROOT),
                f"concurrent commit trial{trial_no} worker{w}",
                "1" if USE_LOCK else "0", str(LOCK_FILE), str(w)]
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        procs.append(p)
    outs = []
    for p in procs:
        out, err = p.communicate(timeout=30)
        try:
            outs.append(json.loads(out.strip().splitlines()[-1]))
        except Exception as e:
            outs.append({"parse_error": str(e), "stdout": out[:300], "stderr": err[:300]})
    return outs


def main():
    stats = {
        "n_trials": N_TRIALS, "n_workers": N_WORKERS, "use_lock": USE_LOCK,
        "committed_count_per_trial": [], "error_types": {}, "index_lock_errors": 0,
        "multiple_committed_same_trial": 0, "zero_committed_trials": 0,
        "lock_timeout_count": 0, "elapsed_all": [],
    }
    for t in range(N_TRIALS):
        outs = run_trial(t)
        committed = [o for o in outs if o.get("committed")]
        stats["committed_count_per_trial"].append(len(committed))
        if len(committed) > 1:
            stats["multiple_committed_same_trial"] += 1
        if len(committed) == 0:
            stats["zero_committed_trials"] += 1
        for o in outs:
            err = o.get("error")
            if err:
                key = "index.lock" if "index.lock" in err else ("LOCK_TIMEOUT" if err == "LOCK_TIMEOUT" else err[:60])
                stats["error_types"][key] = stats["error_types"].get(key, 0) + 1
                if "index.lock" in err:
                    stats["index_lock_errors"] += 1
                if err == "LOCK_TIMEOUT":
                    stats["lock_timeout_count"] += 1
            if o.get("elapsed") is not None:
                stats["elapsed_all"].append(o["elapsed"])
    if stats["elapsed_all"]:
        stats["elapsed_avg"] = sum(stats["elapsed_all"]) / len(stats["elapsed_all"])
        stats["elapsed_max"] = max(stats["elapsed_all"])
    del stats["elapsed_all"]
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
