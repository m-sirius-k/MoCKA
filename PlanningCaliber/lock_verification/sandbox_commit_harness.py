"""
sandbox_commit_harness.py
検証専用スクリプト。本番 governance/mocka_git_safe_commit.py のロジック
(git add -> git diff --cached --quiet判定 -> git commit)を、リポジトリパスのみ
差し替え可能な形でコピーしたもの。本番ファイルは一切編集していない。
対象リポジトリは常に呼び出し側が指定する sandbox_repo のみ。push は行わない。
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


def sandbox_git_commit(root: Path, message: str, use_lock: bool, lock_path: Path = None,
                        lock_timeout: float = 5.0, worker_id: int = 0):
    """本番mocka_git_safe_commit()のgit add-A/commit部分のみを模したロジック。
    use_lock=Trueの場合、簡易ファイルロック(open with O_CREAT|O_EXCL相当)を追加する。
    候補1(ファイルロック)の検証用。"""
    t0 = time.time()
    lock_acquired = None
    lock_wait_time = None

    if use_lock:
        lock_wait_start = time.time()
        acquired = False
        while time.time() - lock_wait_start < lock_timeout:
            try:
                fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(worker_id).encode())
                os.close(fd)
                acquired = True
                break
            except FileExistsError:
                time.sleep(0.01)
        lock_wait_time = time.time() - lock_wait_start
        lock_acquired = acquired
        if not acquired:
            return {"worker_id": worker_id, "committed": False,
                    "error": "LOCK_TIMEOUT", "lock_wait_time": lock_wait_time,
                    "lock_acquired": False, "elapsed": time.time() - t0}

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
                hash_res = _run(["git", "log", "--format=%H", "-1"], root)
                result = {"worker_id": worker_id, "committed": True,
                          "error": None, "commit_hash": hash_res.stdout.strip()}
    finally:
        if use_lock and lock_acquired:
            try:
                os.remove(str(lock_path))
            except FileNotFoundError:
                pass

    result["lock_wait_time"] = lock_wait_time
    result["lock_acquired"] = lock_acquired
    result["elapsed"] = time.time() - t0
    return result


if __name__ == "__main__":
    root = Path(sys.argv[1])
    message = sys.argv[2]
    use_lock = sys.argv[3] == "1"
    lock_path = Path(sys.argv[4]) if len(sys.argv) > 4 else None
    worker_id = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    res = sandbox_git_commit(root, message, use_lock, lock_path, worker_id=worker_id)
    print(json.dumps(res))
