"""
schedule_offset_collision.py
TODO_414関連 - 候補2(スケジュールずらし方式)の実測専用スクリプト。
app.pyの日次seal(固定時刻A)とwatchdog_mocka.pyの日次seal(固定時刻B、Aとは
意図的にずらしてある)、およびAUTO_SEAL_50EVT(時刻非依存のイベント件数トリガーC)
の3種を模した3プロセスを、圧縮した疑似1日(CYCLE秒)の中で動かす。
Cの発火時刻は毎試行ランダム化する(時刻非依存トリガーが実際にいつ発火するか
制御できないことを模す)。ロックは一切導入しない(TODO_414が指摘する現状の
構造そのものを再現するため)。sandbox_repo/lock_verification配下のみで完結し、
本番コード・本番events.dbには一切触れない。
「時刻をずらすこと自体」が競合防止として機能するかどうかの結論はここでは
出さない(衝突発生率の実測値のみ出力)。
"""
import json
import random
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(r"C:\Users\sirok\MoCKA\PlanningCaliber\lock_verification\sandbox_repo")
HARNESS = Path(r"C:\Users\sirok\MoCKA\PlanningCaliber\lock_verification\sandbox_commit_harness.py")

CYCLE = 1.0          # 圧縮した疑似1日の長さ(秒)
T_A = 0.0            # 固定時刻トリガーA(疑似"0時"相当)のオフセット
T_B = 0.5            # 固定時刻トリガーB(疑似"3時"相当)のオフセット。Aとは意図的にずらしてある
COLLISION_WINDOW = 0.12  # このオフセット差以内なら「時刻的に近接」と分類する(実測用の分類軸であり判定基準ではない)
N_TRIALS = int(sys.argv[1]) if len(sys.argv) > 1 else 100
SCHEDULE_LEAD = 0.3  # 各試行でトリガー開始までの助走時間


def reset_trial_state(trial_no):
    (ROOT / "dummy.txt").write_text(f"trial {trial_no} {time.time()}\n", encoding="utf-8")


LABEL_WORKER_ID = {"A_fixed_time": 0, "B_fixed_time": 1, "C_event_count": 2}


def _fire_at(t0, offset, label, trial_no, outs, lock):
    now = time.perf_counter()
    target = t0 + offset
    while now < target:
        remaining = target - now
        time.sleep(min(remaining, 0.005))
        now = time.perf_counter()
    fire_time = time.perf_counter()
    args = [sys.executable, str(HARNESS), str(ROOT),
            f"schedule_offset trial{trial_no} {label}", "0", "", str(LABEL_WORKER_ID[label])]
    p = subprocess.run(args, capture_output=True, text=True, timeout=15)
    try:
        out = json.loads(p.stdout.strip().splitlines()[-1])
    except Exception as e:
        out = {"parse_error": str(e), "stdout": p.stdout[:300], "stderr": p.stderr[:300]}
    out["label"] = label
    out["fire_offset_actual"] = fire_time - t0
    with lock:
        outs.append(out)


def run_trial(trial_no):
    reset_trial_state(trial_no)
    t_c = random.uniform(0, CYCLE)
    near_a = abs(t_c - T_A) < COLLISION_WINDOW
    near_b = abs(t_c - T_B) < COLLISION_WINDOW
    outs = []
    lock = threading.Lock()
    t0 = time.perf_counter() + SCHEDULE_LEAD
    threads = [
        threading.Thread(target=_fire_at, args=(t0, T_A, "A_fixed_time", trial_no, outs, lock)),
        threading.Thread(target=_fire_at, args=(t0, T_B, "B_fixed_time", trial_no, outs, lock)),
        threading.Thread(target=_fire_at, args=(t0, t_c, "C_event_count", trial_no, outs, lock)),
    ]
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    return {"t_c": t_c, "near_a": near_a, "near_b": near_b, "outs": outs}


def main():
    stats = {
        "n_trials": N_TRIALS, "cycle": CYCLE, "t_a": T_A, "t_b": T_B,
        "collision_window": COLLISION_WINDOW,
        "committed_count_per_trial": [], "error_types": {}, "index_lock_errors": 0,
        "multiple_committed_same_trial": 0, "zero_committed_trials": 0,
        "near_trials_count": 0, "near_trials_with_collision": 0,
        "far_trials_count": 0, "far_trials_with_collision": 0,
        "elapsed_all": [],
    }
    for t in range(N_TRIALS):
        trial = run_trial(t)
        outs = trial["outs"]
        committed = [o for o in outs if o.get("committed")]
        stats["committed_count_per_trial"].append(len(committed))
        trial_has_error = False
        if len(committed) > 1:
            stats["multiple_committed_same_trial"] += 1
            trial_has_error = True
        if len(committed) == 0:
            stats["zero_committed_trials"] += 1
        for o in outs:
            err = o.get("error")
            if err:
                trial_has_error = True
                key = "index.lock" if "index.lock" in err else err[:60]
                stats["error_types"][key] = stats["error_types"].get(key, 0) + 1
                if "index.lock" in err:
                    stats["index_lock_errors"] += 1
            if o.get("elapsed") is not None:
                stats["elapsed_all"].append(o["elapsed"])
        is_near = trial["near_a"] or trial["near_b"]
        if is_near:
            stats["near_trials_count"] += 1
            if trial_has_error:
                stats["near_trials_with_collision"] += 1
        else:
            stats["far_trials_count"] += 1
            if trial_has_error:
                stats["far_trials_with_collision"] += 1
    if stats["elapsed_all"]:
        stats["elapsed_avg"] = sum(stats["elapsed_all"]) / len(stats["elapsed_all"])
        stats["elapsed_max"] = max(stats["elapsed_all"])
    del stats["elapsed_all"]
    stats["total_collision_trials"] = stats["multiple_committed_same_trial"]
    stats["total_error_trials_any_kind"] = (
        stats["near_trials_with_collision"] + stats["far_trials_with_collision"]
    )
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
