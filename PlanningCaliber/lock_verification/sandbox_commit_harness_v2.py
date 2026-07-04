"""
sandbox_commit_harness_v2.py
工程4: H1-2(ロック残留による永久ブロック)に対する修繕案の検証専用スクリプト。
v1との差分: ロックファイルにPIDと取得時刻を書き込み、新規取得試行時に
既存ロックが stale_threshold 秒より古い場合は強制的に破棄して取得する
(stale lock breaking)。本番コードには一切影響しない、v1のコピー+修正。
"""
import subprocess
import sys
import time
import os
import json
from pathlib import Path


def _run(cmd, cwd):
    return subprocess.run(
        cmd, cwd=str(cwd), capture_output=True, text=True,
        encoding="utf-8", errors="replace"
    )


def _lock_is_stale(lock_path: Path, stale_threshold: float) -> bool:
    try:
        age = time.time() - lock_path.stat().st_mtime
        return age > stale_threshold
    except FileNotFoundError:
        return False


def sandbox_git_commit_v2(root: Path, message: str, lock_path: Path,
                           lock_timeout: float = 5.0, stale_threshold: float = 2.0,
                           worker_id: int = 0):
    t0 = time.time()
    lock_wait_start = time.time()
    acquired = False
    broke_stale_lock = False
    while time.time() - lock_wait_start < lock_timeout:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, f"{os.getpid()}:{worker_id}".encode())
            os.close(fd)
            acquired = True
            break
        except FileExistsError:
            if _lock_is_stale(lock_path, stale_threshold):
                try:
                    lock_path.unlink()
                    broke_stale_lock = True
                except FileNotFoundError:
                    pass
                continue
            time.sleep(0.01)
    lock_wait_time = time.time() - lock_wait_start

    if not acquired:
        return {"worker_id": worker_id, "committed": False, "error": "LOCK_TIMEOUT",
                "lock_wait_time": lock_wait_time, "broke_stale_lock": broke_stale_lock,
                "elapsed": time.time() - t0}

    try:
        _run(["git", "add", "-A"], root)
        diff_check = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=str(root))
        if diff_check.returncode == 0:
            result = {"worker_id": worker_id, "committed": False, "error": None,
                      "note": "no staged changes"}
        else:
            commit_res = _run(["git", "commit", "-m", message], root)
            if commit_res.returncode != 0:
                result = {"worker_id": worker_id, "committed": False,
                          "error": commit_res.stderr.strip()[:300]}
            else:
                result = {"worker_id": worker_id, "committed": True, "error": None}
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass

    result["lock_wait_time"] = lock_wait_time
    result["broke_stale_lock"] = broke_stale_lock
    result["elapsed"] = time.time() - t0
    return result


if __name__ == "__main__":
    root = Path(sys.argv[1])
    message = sys.argv[2]
    lock_path = Path(sys.argv[3])
    worker_id = int(sys.argv[4])
    res = sandbox_git_commit_v2(root, message, lock_path, worker_id=worker_id)
    print(json.dumps(res))
