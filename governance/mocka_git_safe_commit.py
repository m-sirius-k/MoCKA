import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
"""
mocka_git_safe_commit.py

全てのgit add/commit/push操作を経由する単一の共有ヘルパー(TODO_364)。
is_core_system_file()をここに一元化し、個別スクリプトでの重複実装・
実装漏れを構造的に防止する(GL7構造的死角への対応、方向性B)。

正本: 本ファイルのis_core_system_file()がCore System File除外ロジックの
唯一の正本である。anchor_update.py/sync_watch.py側の同名ロジックは
本ヘルパーからのimportに置き換え、重複定義はしないこと。

運用ルール(push=Trueについて): 本ヘルパーはpushを内部で強制しない
(デフォルトpush=False)。push=Trueで呼ぶ場合は、呼び出し元が
verify_all.py等の検証ステップを経由した上で明示的に呼ぶこと。
検証を経由しないpush=True呼出を新規に追加しないこと(TODO_364運用ルール)。
"""
import subprocess
from pathlib import Path

ROOT = Path(r"C:\Users\sirok\MoCKA")

# Core System File Change Approval(Human Gate)対象。
# 自動シール(AUTO_SEAL_50EVT等)が無承認でこれらの変更を確定させてしまう
# 事故が2026-06-25に発生したため、対象は無条件git add -Aから除外し、
# 未コミットのまま人間承認待ちとして残す(TODO_347governance修正)。
CORE_SYSTEM_DIRS = ("phi_os/", "interface/", "structural/", "gateway/")
CORE_SYSTEM_FILES_EXTRA = (
    "app.py", "index.html", "scripts/ledger/anchor_update.py",
    "PlanningCaliber/workshop/mocka-cloudflare/sync_watch.py",
)
# TODO_370(根本修正): workshop配下はTODO_354でPrivateリポジトリ
# (mocka-workshop-private)管理に切り替わったため、拡張子を問わず
# 無条件でMoCKA本体の自動add対象から除外する。
PRIVATE_REPO_DIRS = ("PlanningCaliber/workshop/",)


def is_core_system_file(path: str) -> bool:
    p = path.replace("\\", "/")
    if p in CORE_SYSTEM_FILES_EXTRA:
        return True
    if p.startswith(PRIVATE_REPO_DIRS):
        return True
    return p.endswith(".py") and p.startswith(CORE_SYSTEM_DIRS)


def _run(cmd, cwd):
    return subprocess.run(
        cmd, cwd=str(cwd), capture_output=True, text=True,
        encoding="utf-8", errors="replace"
    )


def has_pending_core_system_changes(root: Path = ROOT):
    """Core System Fileが未コミット(staged/unstaged問わず)で存在するか確認する。"""
    result = _run(["git", "status", "--porcelain"], root)
    for line in result.stdout.splitlines():
        path = line[3:].strip().replace("\\", "/")
        if is_core_system_file(path):
            return True, path
    return False, None


def mocka_git_safe_commit(paths=None, message="MoCKA auto commit",
                           push=False, root: Path = ROOT,
                           human_gate_override_event_id: str = None):
    """
    git add/commit/(任意でpush)を、Core System File除外を必ず通した上で実行する。

    paths: None なら `git add -A`(全変更)。リスト指定ならそのパスのみadd
           (sync_watch.pyのGIT_TARGETS方式に相当)。
    message: commitメッセージ。
    push: Trueの場合のみ `git push origin main` を実行する。デフォルトFalse。
          push=Trueは検証ステップ(例: verify_all.py)を経由した呼び出し元からのみ
          使用すること(本ファイル冒頭の運用ルール参照)。
    human_gate_override_event_id: Core System File Human Gateの明示的な人間承認
          オーバーライド(2026-07-02 きむら博士裁定, Phase1=チャット承認方式)。
          承認の根拠となったPHL event_id(mocka_write_eventで記録済みのもの)を渡した
          場合のみ、Core System Fileを除外せずcommitに含める(commitメッセージに
          event_idを埋め込み監査trailを保持する)。未指定時は従来通りfail closed(除外)。
          Phase2(UI承認, TODO_207)稼働後は本パラメータの運用方法を見直すこと。

    戻り値: dict(
        committed: bool,            # 実際にcommitが行われたか
        excluded: list[str],        # Core System Fileとしてunstageされたパス
        commit_hash: str|None,      # commit後のHEADハッシュ(commit時のみ)
        pushed: bool,               # push実行有無
        error: str|None,            # エラー発生時のメッセージ
    )
    """
    result = {"committed": False, "excluded": [], "commit_hash": None,
              "pushed": False, "error": None}
    try:
        if paths:
            _run(["git", "add"] + list(paths), root)
        else:
            _run(["git", "add", "-A"], root)

        staged = _run(["git", "diff", "--cached", "--name-only"], root)
        staged_files = staged.stdout.splitlines()
        core_files = [f for f in staged_files if is_core_system_file(f)]

        if core_files and not human_gate_override_event_id:
            _run(["git", "restore", "--staged", "--"] + core_files, root)
            result["excluded"] = core_files
            print(f"[mocka_git_safe_commit] {len(core_files)} core system file(s) "
                  f"excluded, pending Human Gate approval:")
            for f in core_files:
                print(f"  - {f}")
        elif core_files and human_gate_override_event_id:
            message = (f"{message}\n\n"
                       f"[HUMAN_GATE_OVERRIDE:Phase1_chat_approval] "
                       f"event_id={human_gate_override_event_id} "
                       f"core_files={','.join(core_files)}")
            print(f"[mocka_git_safe_commit] {len(core_files)} core system file(s) "
                  f"included via Phase1 chat-approval override "
                  f"(event_id={human_gate_override_event_id}):")
            for f in core_files:
                print(f"  - {f}")

        diff_check = subprocess.run(
            ["git", "diff", "--cached", "--quiet"], cwd=str(root)
        )
        if diff_check.returncode == 0:
            print("[mocka_git_safe_commit] no staged changes, skip commit")
            return result

        commit_res = _run(["git", "commit", "-m", message], root)
        print(commit_res.stdout.strip() or "nothing to commit")
        if commit_res.returncode != 0:
            result["error"] = commit_res.stderr.strip()
            return result

        result["committed"] = True
        hash_res = _run(["git", "log", "--format=%H", "-1"], root)
        result["commit_hash"] = hash_res.stdout.strip()

        if push:
            push_res = _run(["git", "push", "origin", "main"], root)
            if push_res.returncode == 0:
                result["pushed"] = True
                print(f"[mocka_git_safe_commit] pushed {result['commit_hash'][:7]}")
            else:
                result["error"] = push_res.stderr.strip()
                print(f"[mocka_git_safe_commit] push failed: {result['error']}")

        return result
    except Exception as e:
        result["error"] = str(e)
        print(f"[mocka_git_safe_commit] GIT_RECORD_FAILED {e}")
        return result
