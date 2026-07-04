"""
commit_latency_experiments.py
TODO_414関連 - 候補2(スケジュールずらし)の追加実測。
schedule_offset_collision.py の100試行結果で、near(時刻近接)よりfar(非近接)の
方が衝突率が高いという逆説的な結果が出た。git commit自体の実行時間が
CYCLE/COLLISION_WINDOWに対して無視できない大きさであることが分かっており、
これがoffset設計より支配的な変数である可能性がある。
本スクリプトは「offset」と「commit latency」を分離して測定するための3実験を
提供する。sandbox_repo/lock_verification配下のみで完結し、本番コード・
本番events.dbには一切触れない。支配変数がどちらかという結論は出さない
(数値のみ出力)。

サブコマンド:
  solo <n>
      単独条件(競合なし)でのcommit latency分布を測定する。
  offset_fixed <pattern:small|large> <n>
      offsetを固定(OFFSET_C_FIXED)し、commit対象の差分サイズを変えてlatencyを
      人為的に変動させ、衝突率を測定する。
  latency_fixed <offset> <n>
      commit対象の差分サイズを固定(小さい差分のみ)し、offsetのみを変えて
      衝突率を測定する。
"""
import json
import secrets
import statistics
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(r"C:\Users\sirok\MoCKA\PlanningCaliber\lock_verification\sandbox_repo")
HARNESS = Path(r"C:\Users\sirok\MoCKA\PlanningCaliber\lock_verification\sandbox_commit_harness.py")

CYCLE = 1.0
T_A = 0.0
T_B = 0.5
OFFSET_C_FIXED = 0.05  # offset_fixed実験で使う固定オフセット(Aに近接=near相当)
SMALL_SIZE = 50
LARGE_SIZE = 200_000
SCHEDULE_LEAD = 0.3

LABEL_WORKER_ID = {"A_fixed_time": 0, "B_fixed_time": 1, "C_variable": 2}


def write_content(trial_no, size_bytes):
    header = f"trial {trial_no} {time.time()}\n"
    body = secrets.token_hex(max(0, (size_bytes - len(header)) // 2))
    (ROOT / "dummy.txt").write_text(header + body, encoding="utf-8")


def _invoke_harness(message, worker_id):
    args = [sys.executable, str(HARNESS), str(ROOT), message, "0", "", str(worker_id)]
    p = subprocess.run(args, capture_output=True, text=True, timeout=30)
    try:
        return json.loads(p.stdout.strip().splitlines()[-1])
    except Exception as e:
        return {"parse_error": str(e), "stdout": p.stdout[:300], "stderr": p.stderr[:300]}


# ---------- 実験1: 単独latency分布 ----------

def measure_solo_latency(n, size_bytes=SMALL_SIZE):
    latencies = []
    for i in range(n):
        write_content(i, size_bytes)
        out = _invoke_harness(f"solo_latency trial{i}", 0)
        if out.get("elapsed") is not None:
            latencies.append(out["elapsed"])
    latencies.sort()
    mid = len(latencies) // 2
    median = latencies[mid] if len(latencies) % 2 == 1 else (latencies[mid - 1] + latencies[mid]) / 2
    return {
        "n": n,
        "size_bytes": size_bytes,
        "collected": len(latencies),
        "mean": statistics.mean(latencies),
        "median": median,
        "max": max(latencies),
        "min": min(latencies),
        "stdev": statistics.stdev(latencies) if len(latencies) > 1 else 0.0,
    }


# ---------- 共通: 3プロセス同時発火 ----------

def _fire_at(t0, offset, label, trial_no, outs, lock):
    now = time.perf_counter()
    target = t0 + offset
    while now < target:
        time.sleep(min(target - now, 0.005))
        now = time.perf_counter()
    out = _invoke_harness(f"trial{trial_no} {label}", LABEL_WORKER_ID[label])
    out["label"] = label
    with lock:
        outs.append(out)


def run_trial(trial_no, t_c, size_bytes):
    write_content(trial_no, size_bytes)
    outs = []
    lock = threading.Lock()
    t0 = time.perf_counter() + SCHEDULE_LEAD
    threads = [
        threading.Thread(target=_fire_at, args=(t0, T_A, "A_fixed_time", trial_no, outs, lock)),
        threading.Thread(target=_fire_at, args=(t0, T_B, "B_fixed_time", trial_no, outs, lock)),
        threading.Thread(target=_fire_at, args=(t0, t_c, "C_variable", trial_no, outs, lock)),
    ]
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    return outs


def aggregate(n_trials, t_c, size_bytes):
    stats = {
        "n_trials": n_trials, "t_c": t_c, "size_bytes": size_bytes,
        "index_lock_errors": 0, "head_lock_errors": 0,
        "error_trials": 0, "zero_committed_trials": 0,
        "multiple_committed_same_trial": 0,
        "elapsed_all": [],
    }
    for t in range(n_trials):
        outs = run_trial(t, t_c, size_bytes)
        committed = [o for o in outs if o.get("committed")]
        if len(committed) == 0:
            stats["zero_committed_trials"] += 1
        if len(committed) > 1:
            stats["multiple_committed_same_trial"] += 1
        trial_has_error = len(committed) > 1
        for o in outs:
            err = o.get("error")
            if err:
                trial_has_error = True
                if "index.lock" in err:
                    stats["index_lock_errors"] += 1
                elif "cannot lock ref" in err:
                    stats["head_lock_errors"] += 1
            if o.get("elapsed") is not None:
                stats["elapsed_all"].append(o["elapsed"])
        if trial_has_error:
            stats["error_trials"] += 1
    elapsed = stats.pop("elapsed_all")
    if elapsed:
        elapsed.sort()
        mid = len(elapsed) // 2
        stats["latency_mean"] = statistics.mean(elapsed)
        stats["latency_median"] = elapsed[mid] if len(elapsed) % 2 == 1 else (elapsed[mid - 1] + elapsed[mid]) / 2
        stats["latency_max"] = max(elapsed)
        stats["latency_min"] = min(elapsed)
        stats["latency_stdev"] = statistics.stdev(elapsed) if len(elapsed) > 1 else 0.0
    return stats


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "solo":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 150
        result = measure_solo_latency(n)
    elif mode == "offset_fixed":
        pattern = sys.argv[2]
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 100
        size_bytes = SMALL_SIZE if pattern == "small" else LARGE_SIZE
        result = aggregate(n, OFFSET_C_FIXED, size_bytes)
        result["pattern"] = pattern
    elif mode == "latency_fixed":
        offset = float(sys.argv[2])
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 100
        result = aggregate(n, offset, SMALL_SIZE)
    else:
        raise SystemExit(f"unknown mode: {mode}")
    print(json.dumps(result, indent=2, ensure_ascii=False))
