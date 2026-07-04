"""
candidate1_stale_redesign.py
TODO_414関連 - 候補1(stale判定再設計)の実測専用スクリプト。
固定閾値方式(sandbox_commit_harness_v2.py)がH1-2(ロック残留)は解消する一方、
正常稼働中プロセスからの誤奪取を発生させることが slow_holder_test.py で
確認された。この誤奪取を避けるため、以下2方式を実装し同一2条件で実測する。

方式A: ハートビート方式
  - ロック保持プロセスが一定間隔(HEARTBEAT_INTERVAL)でロックファイルの
    heartbeat_tsを更新し続ける。checker側は「最後のheartbeatからの経過時間」が
    MISSED_THRESHOLDを超えた場合のみstale判定する(保持開始からの総経過時間では判定しない)。

方式B: PID生存確認方式
  - ロックファイルにPIDを記録する。checker側はOS上でそのPIDが実際に
    稼働中かを確認する(Windows: OpenProcess+GetExitCodeProcess)。
    稼働中ならどれだけ時間が経過していてもstale扱いしない。
    稼働していなければ即座にstale。

いずれもsandbox_repo/lock_verification配下のみで完結し、本番コードには
一切触れない。両方式の優劣判断はここでは行わない(実測結果のみ出力)。
"""
import ctypes
import json
import multiprocessing
import os
import time
from pathlib import Path

LOCK_DIR = Path(r"C:\Users\sirok\MoCKA\PlanningCaliber\lock_verification")
HEARTBEAT_INTERVAL = 0.3
MISSED_THRESHOLD = 1.0  # ハートビート方式: 最終heartbeatからこの秒数途絶えたらstale
LEGIT_WORK_DURATION = 3.0  # 「正常に時間がかかっている保持者」の作業時間
CHECKER_START_DELAY = 0.5
CHECKER_POLL_INTERVAL = 0.05
CHECKER_TIMEOUT = 6.0

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
STILL_ACTIVE = 259


def pid_is_alive(pid: int) -> bool:
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return False
    exit_code = ctypes.c_ulong()
    kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
    kernel32.CloseHandle(handle)
    return exit_code.value == STILL_ACTIVE


def force_kill(pid: int):
    PROCESS_TERMINATE = 0x0001
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
    if handle:
        kernel32.TerminateProcess(handle, 1)
        kernel32.CloseHandle(handle)


# ---------- 方式A: ハートビート ----------

def hb_holder_legit(lock_path_str, ready_flag):
    lock_path = Path(lock_path_str)
    fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, f"{os.getpid()}:legit:{time.time()}".encode())
    os.close(fd)
    ready_flag.value = 1
    t_end = time.time() + LEGIT_WORK_DURATION
    while time.time() < t_end:
        time.sleep(HEARTBEAT_INTERVAL)
        try:
            lock_path.write_text(f"{os.getpid()}:legit:{time.time()}")
        except FileNotFoundError:
            break  # 奪われた場合はそこで終了(誤奪取が起きた証拠)
    try:
        lock_path.unlink()
    except FileNotFoundError:
        pass


def hb_holder_crash_seed(lock_path_str, ready_flag):
    """ロックを取得してheartbeatを2回だけ打ち、その後は完全に停止する
    (プロセス自体は生き続けるが、heartbeat更新を止める=クラッシュ挙動を模す)。
    実際のプロセス死亡ケースは別途force_killで検証する。"""
    lock_path = Path(lock_path_str)
    fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, f"{os.getpid()}:crashseed:{time.time()}".encode())
    os.close(fd)
    ready_flag.value = 1
    time.sleep(HEARTBEAT_INTERVAL)
    lock_path.write_text(f"{os.getpid()}:crashseed:{time.time()}")
    time.sleep(999)  # ここでforce_killされる想定


def hb_checker(lock_path_str, result_dict):
    lock_path = Path(lock_path_str)
    time.sleep(CHECKER_START_DELAY)
    start = time.time()
    broke_it = False
    acquired = False
    while time.time() - start < CHECKER_TIMEOUT:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, f"{os.getpid()}:checker:{time.time()}".encode())
            os.close(fd)
            acquired = True
            break
        except FileExistsError:
            try:
                content = lock_path.read_text()
                hb_ts = float(content.split(":")[-1])
                age_since_heartbeat = time.time() - hb_ts
            except (FileNotFoundError, ValueError, IndexError):
                age_since_heartbeat = 0.0
            if age_since_heartbeat > MISSED_THRESHOLD:
                try:
                    lock_path.unlink()
                    broke_it = True
                except FileNotFoundError:
                    pass
                continue
            time.sleep(CHECKER_POLL_INTERVAL)
    result_dict["acquired"] = acquired
    result_dict["broke_stale_lock"] = broke_it
    result_dict["elapsed"] = time.time() - start


def run_heartbeat_crash_trial():
    lock_path = LOCK_DIR / ".cand1_hb_crash.lock"
    if lock_path.exists():
        lock_path.unlink()
    ready = multiprocessing.Value("i", 0)
    mgr = multiprocessing.Manager()
    result = mgr.dict()
    p_holder = multiprocessing.Process(target=hb_holder_crash_seed, args=(str(lock_path), ready))
    p_holder.start()
    while ready.value == 0:
        time.sleep(0.01)
    time.sleep(HEARTBEAT_INTERVAL * 2 + 0.1)  # heartbeatを1-2回打たせてから殺す
    t_kill = time.time()
    force_kill(p_holder.pid)
    p_holder.join(timeout=2)
    p_checker = multiprocessing.Process(target=hb_checker, args=(str(lock_path), result))
    # checker開始は「殺した瞬間」からの遅延で測るためCHECKER_START_DELAYを0扱いに寄せず、
    # ここでは既存仕様のCHECKER_START_DELAY(0.5s)をそのまま使う(H1-2再現条件に合わせる)
    p_checker.start()
    p_checker.join(timeout=CHECKER_TIMEOUT + 2)
    res = dict(result)
    res["time_from_kill_to_detect"] = None
    if lock_path.exists():
        lock_path.unlink()
    return res


def run_heartbeat_legit_trial():
    lock_path = LOCK_DIR / ".cand1_hb_legit.lock"
    if lock_path.exists():
        lock_path.unlink()
    ready = multiprocessing.Value("i", 0)
    mgr = multiprocessing.Manager()
    result = mgr.dict()
    p_holder = multiprocessing.Process(target=hb_holder_legit, args=(str(lock_path), ready))
    p_checker = multiprocessing.Process(target=hb_checker, args=(str(lock_path), result))
    p_holder.start()
    p_checker.start()
    p_holder.join(timeout=LEGIT_WORK_DURATION + 3)
    p_checker.join(timeout=CHECKER_TIMEOUT + 2)
    res = dict(result)
    if lock_path.exists():
        lock_path.unlink()
    return res


# ---------- 方式B: PID生存確認 ----------

def pid_holder_legit(lock_path_str, ready_flag):
    lock_path = Path(lock_path_str)
    fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, f"{os.getpid()}:legit".encode())
    os.close(fd)
    ready_flag.value = 1
    time.sleep(LEGIT_WORK_DURATION)
    try:
        lock_path.unlink()
    except FileNotFoundError:
        pass


def pid_holder_crash_seed(lock_path_str, ready_flag):
    lock_path = Path(lock_path_str)
    fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, f"{os.getpid()}:crashseed".encode())
    os.close(fd)
    ready_flag.value = 1
    time.sleep(999)  # ここでforce_killされる想定


def pid_checker(lock_path_str, result_dict):
    lock_path = Path(lock_path_str)
    time.sleep(CHECKER_START_DELAY)
    start = time.time()
    broke_it = False
    acquired = False
    while time.time() - start < CHECKER_TIMEOUT:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, f"{os.getpid()}:checker".encode())
            os.close(fd)
            acquired = True
            break
        except FileExistsError:
            try:
                content = lock_path.read_text()
                holder_pid = int(content.split(":")[0])
                alive = pid_is_alive(holder_pid)
            except (FileNotFoundError, ValueError, IndexError):
                alive = False
            if not alive:
                try:
                    lock_path.unlink()
                    broke_it = True
                except FileNotFoundError:
                    pass
                continue
            time.sleep(CHECKER_POLL_INTERVAL)
    result_dict["acquired"] = acquired
    result_dict["broke_stale_lock"] = broke_it
    result_dict["elapsed"] = time.time() - start


def run_pid_crash_trial():
    lock_path = LOCK_DIR / ".cand1_pid_crash.lock"
    if lock_path.exists():
        lock_path.unlink()
    ready = multiprocessing.Value("i", 0)
    mgr = multiprocessing.Manager()
    result = mgr.dict()
    p_holder = multiprocessing.Process(target=pid_holder_crash_seed, args=(str(lock_path), ready))
    p_holder.start()
    while ready.value == 0:
        time.sleep(0.01)
    time.sleep(0.2)
    force_kill(p_holder.pid)
    p_holder.join(timeout=2)
    p_checker = multiprocessing.Process(target=pid_checker, args=(str(lock_path), result))
    p_checker.start()
    p_checker.join(timeout=CHECKER_TIMEOUT + 2)
    res = dict(result)
    if lock_path.exists():
        lock_path.unlink()
    return res


def run_pid_legit_trial():
    lock_path = LOCK_DIR / ".cand1_pid_legit.lock"
    if lock_path.exists():
        lock_path.unlink()
    ready = multiprocessing.Value("i", 0)
    mgr = multiprocessing.Manager()
    result = mgr.dict()
    p_holder = multiprocessing.Process(target=pid_holder_legit, args=(str(lock_path), ready))
    p_checker = multiprocessing.Process(target=pid_checker, args=(str(lock_path), result))
    p_holder.start()
    p_checker.start()
    p_holder.join(timeout=LEGIT_WORK_DURATION + 3)
    p_checker.join(timeout=CHECKER_TIMEOUT + 2)
    res = dict(result)
    if lock_path.exists():
        lock_path.unlink()
    return res


if __name__ == "__main__":
    multiprocessing.freeze_support()
    out = {
        "params": {
            "HEARTBEAT_INTERVAL": HEARTBEAT_INTERVAL,
            "MISSED_THRESHOLD": MISSED_THRESHOLD,
            "LEGIT_WORK_DURATION": LEGIT_WORK_DURATION,
            "CHECKER_START_DELAY": CHECKER_START_DELAY,
        },
        "heartbeat_crash": run_heartbeat_crash_trial(),
        "heartbeat_legit": run_heartbeat_legit_trial(),
        "pid_crash": run_pid_crash_trial(),
        "pid_legit": run_pid_legit_trial(),
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
