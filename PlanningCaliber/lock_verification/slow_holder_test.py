"""
工程4追加検証: stale_threshold方式の副作用確認。
worker_A: ロック取得後、意図的に3秒間"作業中"を装う(実際には正常に稼働中、クラッシュではない)。
worker_B: 0.5秒後に同じロックへ取得を試みる(stale_threshold=2.0)。
worker_Aがまだ正常に保持している最中に、worker_Bがstaleと誤判定してロックを
奪い取ってしまうか(=誤検知による二重commitの可能性)を実測する。
"""
import os
import sys
import time
import multiprocessing
from pathlib import Path

LOCK_PATH = Path(r"C:\Users\sirok\MoCKA\PlanningCaliber\lock_verification\.sandbox_git.lock")


def _lock_is_stale(lock_path, stale_threshold):
    try:
        return time.time() - lock_path.stat().st_mtime > stale_threshold
    except FileNotFoundError:
        return False


def worker_a_slow_legit_holder():
    fd = os.open(str(LOCK_PATH), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, b"worker_A_legit")
    os.close(fd)
    print(f"[A] lock acquired at {time.time():.2f}, working for 3s (legit, not crashed)")
    time.sleep(3.0)  # 正常な作業中(クラッシュではない)
    still_mine = False
    try:
        content = LOCK_PATH.read_text()
        still_mine = "worker_A" in content
    except FileNotFoundError:
        still_mine = False
    print(f"[A] finished work. lock still exists and is mine: {still_mine}")
    try:
        LOCK_PATH.unlink()
    except FileNotFoundError:
        print("[A] WARNING: lock already gone when I tried to release it (someone else removed it)")


def worker_b_stale_checker(stale_threshold=2.0, lock_timeout=5.0):
    time.sleep(0.5)
    start = time.time()
    broke_it = False
    acquired = False
    while time.time() - start < lock_timeout:
        try:
            fd = os.open(str(LOCK_PATH), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, b"worker_B")
            os.close(fd)
            acquired = True
            break
        except FileExistsError:
            if _lock_is_stale(LOCK_PATH, stale_threshold):
                print(f"[B] at t={time.time()-start:.2f}s judged lock as STALE (age>{stale_threshold}s) -> breaking it")
                try:
                    LOCK_PATH.unlink()
                    broke_it = True
                except FileNotFoundError:
                    pass
                continue
            time.sleep(0.05)
    print(f"[B] acquired={acquired} broke_stale_lock={broke_it}")


if __name__ == "__main__":
    if LOCK_PATH.exists():
        LOCK_PATH.unlink()
    pa = multiprocessing.Process(target=worker_a_slow_legit_holder)
    pb = multiprocessing.Process(target=worker_b_stale_checker)
    pa.start()
    pb.start()
    pa.join()
    pb.join()
