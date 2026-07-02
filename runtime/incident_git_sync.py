import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import subprocess
import os
import sys

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
LEDGER = os.path.join(BASE,"runtime","incident_ledger.json")

sys.path.insert(0, os.path.join(BASE, "governance"))
from mocka_git_safe_commit import mocka_git_safe_commit  # noqa: E402

# 2026-07-02 棚卸し確認: この関数(commit_incident)を呼び出しているコードは
# リポジトリ内に存在しない(呼び出し元0件、死経路)。mocka_git_safe_commit()自体は
# 正しく呼べる状態だが、実行トリガーが無いため現状は未実行。
# 削除は判断せず、明示化のみ(2026-07-02 きむら博士確認)。
# TODO_364: git add/commit/pushをmocka_git_safe_commit経由に統一。
def commit_incident():
    result = mocka_git_safe_commit(
        paths=[LEDGER], message="MoCKA incident update",
        push=True, root=BASE
    )
    if result["error"]:
        print("GIT_RECORD_FAILED", result["error"])
    else:
        print("INCIDENT_GIT_RECORDED")

if __name__ == "__main__":
    commit_incident()
