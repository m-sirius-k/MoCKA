"""
mocka_auto_record.py — TODO_153 + Bash/PowerShell裏口対応
===========================================================
Claude Code PostToolUse フックから呼ばれ、ファイル変更操作後に
自動で mocka_write_event を発火する。

対象ツール: Write, Edit, NotebookEdit, MultiEdit, Bash, PowerShell

Bash/PowerShell の場合: コマンド文字列にファイル書き込みパターンが
含まれる場合のみ記録する（ls, git status等の非破壊操作はスキップ）。

呼び出し形式（Claude Code hooks が stdin に JSON を渡す）:
{
  "tool_name": "Write",
  "tool_input": {"file_path": "...", "content": "..."},
  "tool_response": {...}
}
"""

import json
import sys
import os
import re
import urllib.request
import urllib.error
import datetime
from pathlib import Path

LOCAL_MCP   = "http://localhost:5002/agent/mocka_write_event"
LOCAL_APP   = "http://localhost:5000/file/register"
_ENDPOINT   = os.environ.get("MOCKA_ENDPOINT", "")
REMOTE_MCP  = f"{_ENDPOINT}/agent/mocka_write_event" if _ENDPOINT else ""

LOG_PATH    = Path(__file__).resolve().parent / "auto_record.log"

# Windows cp932コンソールでのUnicodeEncodeError防止（PostToolUseフックを落とさない）
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WATCH_TOOLS = {"Write", "Edit", "NotebookEdit", "MultiEdit", "Bash", "PowerShell"}
SHELL_TOOLS = {"Bash", "PowerShell"}

# ファイル書き込みを示すコマンドパターン
# 誤検知より検知漏れを優先（疑わしい場合は記録する方針）
_WRITE_PATTERNS = re.compile(
    r"""
    (?:
        >|>>                                        # リダイレクト
        | \bcp\s                                    # cp (コピー)
        | \bmv\s                                    # mv (移動)
        | \bscp\s                                   # scp
        | \brm\s                                    # rm (削除もファイル変更)
        | sqlite3\b.*?\b(?:INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\b  # SQLite書き込み
        | \bpython\b.*?open\s*\(.*?[\"']w[\"']     # python open write mode
        | \bpython\b.*?\.write\s*\(                # python .write()
        | Set-Content\b                             # PowerShell Set-Content
        | Out-File\b                                # PowerShell Out-File
        | Add-Content\b                             # PowerShell Add-Content
        | New-Item\b.*?-ItemType\s+File            # PowerShell New-Item File
        | Copy-Item\b                               # PowerShell Copy-Item
        | Move-Item\b                               # PowerShell Move-Item
        | Remove-Item\b                             # PowerShell Remove-Item
        | Rename-Item\b                             # PowerShell Rename-Item
        | \btouch\s                                 # touch
        | \bchmod\s                                 # chmod
        | \bmkdir\b                                 # mkdir
        | \bsed\s+-i\b                              # sed -i (in-place)
        | \bawk\b.*?>                               # awk with redirect
        | \becho\b.*?>                              # echo with redirect
        | \bcat\b.*?>                               # cat with redirect
        | \bprintf\b.*?>                            # printf with redirect
        | \btee\b                                   # tee
        | \bgit\b.*?\b(?:commit|rm|add|reset|checkout\s+-f|restore\b)  # git write ops
        | \bnohup\b                                 # nohup (サーバー起動＝状態変更)
        | \bpip\s+install\b                         # pip install
        | \bnpm\s+install\b                         # npm install
        | \bwrangler\s+deploy\b                     # wrangler deploy
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)


def _log(line: str):
    try:
        ts = datetime.datetime.now().isoformat()
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {line}\n")
    except Exception:
        pass


def _post(url: str, payload: bytes, timeout: int = 3) -> dict:
    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _extract_file_path(tool_name: str, tool_input: dict) -> str:
    if tool_name == "Write":
        return tool_input.get("file_path", "")
    if tool_name == "Edit":
        return tool_input.get("file_path", "")
    if tool_name == "NotebookEdit":
        return tool_input.get("notebook_path", "")
    if tool_name == "MultiEdit":
        return tool_input.get("file_path", "")
    return tool_input.get("file_path", tool_input.get("path", ""))


def _count_lines(tool_name: str, tool_input: dict) -> int | None:
    if tool_name == "Write":
        content = tool_input.get("content", "")
        return content.count("\n") + 1 if content else None
    return None


def _should_record_shell(command: str) -> tuple[bool, str]:
    """
    Bash/PowerShellコマンドがファイル書き込みを伴うか判定する。

    Returns:
        (should_record, reason)
        reason: マッチしたパターンまたはスキップ理由

    限界（誤検知・漏れ）:
    - 誤検知: コメント内のパターン、echo ">" のような文字列リテラル内の > 等
    - 検知漏れ: 変数展開後に書き込みとなるコマンド、
      カスタム関数/スクリプト呼び出し（python myscript.py など引数なし）
    - 方針: 漏れより誤検知を許容（疑わしければ記録する）
    """
    m = _WRITE_PATTERNS.search(command)
    if m:
        return True, f"pattern={m.group(0)[:40].strip()!r}"
    return False, "no_write_pattern"


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    tool_name  = data.get("tool_name", os.environ.get("CLAUDE_TOOL_NAME", ""))
    tool_input = data.get("tool_input", {})

    if tool_name not in WATCH_TOOLS:
        sys.exit(0)

    # Bash/PowerShell: コマンド文字列でファイル変更を判定
    if tool_name in SHELL_TOOLS:
        command = tool_input.get("command", "")
        should_record, reason = _should_record_shell(command)
        if not should_record:
            _log(f"SKIP tool={tool_name} reason={reason} cmd={command[:80]!r}")
            sys.exit(0)
        # Bash/PowerShellの場合、file_pathはコマンド文字列を短縮して使う
        fname    = f"[{tool_name}] {command[:60].strip()}"
        now      = datetime.datetime.now().isoformat()
        title    = f"CHANGE_DONE: {tool_name} (shell write) [{reason}]"
        desc_parts = [f"コマンド: {command[:200]}", f"ツール: {tool_name}", f"検知パターン: {reason}", f"timestamp: {now}"]
        description = " | ".join(desc_parts)
    else:
        file_path   = _extract_file_path(tool_name, tool_input)
        lines_after = _count_lines(tool_name, tool_input)
        if not file_path:
            sys.exit(0)
        fname = file_path.replace("\\", "/").split("/")[-1]
        now   = datetime.datetime.now().isoformat()
        title = f"CHANGE_DONE: {tool_name} -> {fname}"
        desc_parts = [f"ファイル: {file_path}", f"ツール: {tool_name}"]
        if lines_after is not None:
            desc_parts.append(f"行数: {lines_after}")
        desc_parts.append(f"timestamp: {now}")
        description = " | ".join(desc_parts)

    payload = json.dumps({
        "title":       title,
        "description": description,
        "tags":        f"auto_record,posttooluse,change_done,{tool_name}",
        "author":      "Claude",
        "why_purpose": "TODO_153: ファイル生成=記録義務",
        "how_trigger": "PostToolUse hook",
    }, ensure_ascii=False).encode("utf-8")

    sent = False
    for url in filter(None, [LOCAL_MCP, REMOTE_MCP if REMOTE_MCP else None]):
        try:
            result = _post(url, payload)
            eid = result.get("event_id", "?")
            print(f"[mocka_auto_record] OK {eid} — {fname}", flush=True)
            _log(f"OK event_id={eid} tool={tool_name} cmd_or_file={fname!r} url={url}")
            sent = True
            break
        except Exception as e:
            print(f"[mocka_auto_record] WARN {url}: {e}", flush=True)
            _log(f"WARN url={url} tool={tool_name} error={e}")

    if not sent:
        print(f"[mocka_auto_record] OFFLINE — {fname} (全エンドポイント失敗)", flush=True)
        _log(f"OFFLINE tool={tool_name} cmd_or_file={fname!r} (記録未送信・作業は継続)")

    sys.exit(0)


if __name__ == "__main__":
    main()
