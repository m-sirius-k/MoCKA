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
import json
import inspect
import datetime
import urllib.request
from pathlib import Path

ROOT = Path(r"C:\Users\sirok\MoCKA")

# TODO_413: mocka_git_safe_commit()をGit操作の制度的責任点(Institutional
# Recording Point)とする。呼び出し元(anchor_update.py/sync_watch.py/
# incident_engine.py/incident_git_sync.py等)には一切手を入れず、本ファイル
# 内部の記録のみでCHANGE_START/CHANGE_DONE相当のLedger記録を完結させる。
_GIT_EVENT_ENDPOINT = "http://localhost:5002/agent/mocka_write_event"
_GIT_EVENT_FALLBACK_LOG = Path(__file__).resolve().parent / "mocka_git_safe_commit_ledger_fallback.log"

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


def _current_branch(root):
    try:
        r = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], root)
        return r.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def _detect_caller():
    """mocka_git_safe_commit()の呼び出し元を、呼び出し元に一切変更を求めず
    スタックから自動検出する(TODO_413: 呼び出し元にmocka_write_eventを
    呼ばせる設計は禁止のため)。"""
    try:
        stack = inspect.stack()
        # stack[0]=_detect_caller, stack[1]=mocka_git_safe_commit, stack[2]=実際の呼び出し元
        if len(stack) > 2:
            f = stack[2]
            return f"{Path(f.filename).name}:{f.lineno}"
    except Exception:
        pass
    return "unknown"


def _record_git_event(title, root, branch, caller, result_state,
                       message=None, commit_hash=None, error=None, extra=None):
    """
    TODO_413完了対応: git commitの開始/成功/失敗/スキップを、呼び出し元の
    実装有無に依存せず本関数の内部呼び出しのみでLedgerへ記録する。
    MoCKAサーバー(localhost:5002)が応答しない場合はfallbackログに書き、
    git操作自体はブロックしない(tools/mocka_auto_record.pyと同じ方針)。
    """
    now = datetime.datetime.now().isoformat()
    desc_parts = [
        "operation=git_commit",
        f"repository={root}",
        f"branch={branch}",
        f"commit_sha={commit_hash or 'N/A'}",
        "actor=script:mocka_git_safe_commit",
        f"caller={caller}",
        f"timestamp={now}",
        f"result={result_state}",
    ]
    if message is not None:
        desc_parts.append(f"commit_message={message!r}")
    if error:
        desc_parts.append(f"error={error}")
    if extra:
        desc_parts.append(extra)
    description = " | ".join(desc_parts)

    payload = json.dumps({
        "title": title,
        "description": description,
        "tags": f"todo_413,git_commit,institutional_recording_point,{result_state}",
        "author": "script:mocka_git_safe_commit",
        "why_purpose": "TODO_413: Git操作の制度的記録(呼び出し元非依存)",
        "how_trigger": f"mocka_git_safe_commit/{caller}",
    }, ensure_ascii=False).encode("utf-8")
    try:
        req = urllib.request.Request(
            _GIT_EVENT_ENDPOINT, data=payload,
            headers={"Content-Type": "application/json"}, method="POST"
        )
        # 2026-07-10実測: /agent/mocka_write_eventの応答は約5秒かかる場合がある
        # (tools/mocka_auto_record.py等の既存timeout=3と同条件で計測、常時fallback
        # に落ちることを確認)。commit経路をブロックしない範囲で確実に記録できる
        # よう、余裕を持たせてtimeout=12とする。
        with urllib.request.urlopen(req, timeout=12) as r:
            body = json.loads(r.read())
        eid = body.get("event_id", "?")
        print(f"[mocka_git_safe_commit] ledger recorded: {eid} ({result_state})")
        return eid
    except Exception as e:
        try:
            with open(_GIT_EVENT_FALLBACK_LOG, "a", encoding="utf-8") as f:
                f.write(f"[{now}] OFFLINE {title} | {description} | send_error={e}\n")
        except Exception:
            pass
        print(f"[mocka_git_safe_commit] WARN ledger record failed ({e}), logged to fallback")
        return None


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
        post_commit_files: list[str],     # commit直後にgit showで確認した実際の構成ファイル
        post_commit_violation: list[str], # 上記のうちis_core_system_file()に該当するもの
                                           # (非空の場合、呼び出し元はCHANGE_DONEではなく
                                           # INCIDENT_CREATE相当として扱うこと)
    )
    """
    result = {"committed": False, "excluded": [], "commit_hash": None,
              "pushed": False, "error": None,
              "post_commit_files": [], "post_commit_violation": []}
    caller = _detect_caller()
    branch = _current_branch(root)
    _record_git_event(
        title="CHANGE_START: git commit 開始",
        root=root, branch=branch, caller=caller,
        result_state="started", message=message,
    )
    try:
        if paths:
            _run(["git", "add"] + list(paths), root)
        else:
            _run(["git", "add", "-A"], root)

        staged = _run(["git", "diff", "--cached", "--name-only"], root)
        staged_files = staged.stdout.splitlines()
        core_files = [f for f in staged_files if is_core_system_file(f)]

        if core_files and not human_gate_override_event_id:
            restore_res = _run(["git", "restore", "--staged", "--"] + core_files, root)
            if restore_res.returncode != 0:
                result["error"] = (f"git restore --staged failed for core system file(s), "
                                   f"commit aborted: {restore_res.stderr.strip()}")
                print(f"[mocka_git_safe_commit] ERROR: {result['error']}")
                _record_git_event(
                    title="CHANGE_FAILED: git commit中断(core system file除外失敗)",
                    root=root, branch=branch, caller=caller,
                    result_state="failure", message=message, error=result["error"],
                )
                return result

            # Post-condition verification (E20260708_6613941345364): don't trust the
            # restore returncode alone, re-read the staged set to confirm exclusion
            # actually took effect before proceeding to commit.
            recheck = _run(["git", "diff", "--cached", "--name-only"], root)
            still_staged = [f for f in recheck.stdout.splitlines() if is_core_system_file(f)]
            if still_staged:
                result["error"] = (f"core system file(s) still staged after restore, "
                                   f"commit aborted: {still_staged}")
                print(f"[mocka_git_safe_commit] ERROR: {result['error']}")
                _record_git_event(
                    title="CHANGE_FAILED: git commit中断(core system file再検証失敗)",
                    root=root, branch=branch, caller=caller,
                    result_state="failure", message=message, error=result["error"],
                )
                return result

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
            _record_git_event(
                title="CHANGE_DONE: git commit スキップ(差分なし)",
                root=root, branch=branch, caller=caller,
                result_state="skipped", message=message,
            )
            return result

        commit_res = _run(["git", "commit", "-m", message], root)
        print(commit_res.stdout.strip() or "nothing to commit")
        if commit_res.returncode != 0:
            result["error"] = commit_res.stderr.strip()
            _record_git_event(
                title="CHANGE_FAILED: git commit失敗",
                root=root, branch=branch, caller=caller,
                result_state="failure", message=message, error=result["error"],
            )
            return result

        result["committed"] = True
        hash_res = _run(["git", "log", "--format=%H", "-1"], root)
        result["commit_hash"] = hash_res.stdout.strip()

        # Standardized post-commit verification (all safe commits, per Phase 4
        # security patch step3): independently re-inspect the actual committed
        # tree (not just the pre-commit staged set) for core system files that
        # should never have landed here. This is a second, independent check
        # in addition to the pre-commit exclusion above.
        show_res = _run(
            ["git", "show", "--name-only", "--format=", result["commit_hash"]], root
        )
        committed_files = [f for f in show_res.stdout.splitlines() if f.strip()]
        result["post_commit_files"] = committed_files
        core_in_commit = [f for f in committed_files if is_core_system_file(f)]
        # Core file presence is only a violation when it wasn't explicitly
        # authorized via human_gate_override_event_id for this call. Authorized
        # inclusions are expected and already carry the event_id in the commit
        # message (see the override branch above).
        result["post_commit_violation"] = (
            [] if human_gate_override_event_id else core_in_commit
        )
        if result["post_commit_violation"]:
            print(f"[mocka_git_safe_commit] POST-COMMIT VIOLATION: core system "
                  f"file(s) present in commit {result['commit_hash'][:7]} despite "
                  f"exclusion (no override was given for this call): "
                  f"{result['post_commit_violation']}. Caller must treat this as "
                  f"an integrity incident, not a normal CHANGE_DONE.")
        elif core_in_commit:
            print(f"[mocka_git_safe_commit] post-commit check OK: "
                  f"{len(committed_files)} file(s) in {result['commit_hash'][:7]}, "
                  f"core system file(s) {core_in_commit} present via authorized "
                  f"override (event_id={human_gate_override_event_id})")
        else:
            print(f"[mocka_git_safe_commit] post-commit check OK: "
                  f"{len(committed_files)} file(s) in {result['commit_hash'][:7]}, "
                  f"no core system file(s) present")

        _record_git_event(
            title=f"CHANGE_DONE: git commit成功 {result['commit_hash'][:7]}",
            root=root, branch=branch, caller=caller,
            result_state="success", message=message, commit_hash=result["commit_hash"],
            extra=(f"files={result['post_commit_files']} | "
                   f"post_commit_violation={result['post_commit_violation']}"),
        )

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
        _record_git_event(
            title="CHANGE_FAILED: git commit例外",
            root=root, branch=branch, caller=caller,
            result_state="failure", message=message, error=str(e),
        )
        return result
