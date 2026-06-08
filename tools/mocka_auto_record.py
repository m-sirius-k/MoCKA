"""
mocka_auto_record.py — TODO_153 実装
=====================================
Claude Code PostToolUse フックから呼ばれ、Edit/Write/NotebookEdit 実行後に
自動で mocka_write_event を発火する。

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
import urllib.request
import urllib.error
import datetime
from pathlib import Path

LOCAL_MCP   = "http://localhost:5002/agent/mocka_write_event"
LOCAL_APP   = "http://localhost:5000/file/register"
_ENDPOINT   = os.environ.get("MOCKA_ENDPOINT", "")
REMOTE_MCP  = f"{_ENDPOINT}/agent/mocka_write_event" if _ENDPOINT else ""

LOG_PATH    = Path(__file__).resolve().parent / "auto_record.log"

WATCH_TOOLS = {"Write", "Edit", "NotebookEdit", "MultiEdit"}


def _log(line: str):
    """記録の成否をローカルログに残す（サーバー落ち時の追跡用、作業はブロックしない）"""
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

    file_path   = _extract_file_path(tool_name, tool_input)
    lines_after = _count_lines(tool_name, tool_input)
    if not file_path:
        sys.exit(0)

    fname = file_path.replace("\\", "/").split("/")[-1]
    now   = datetime.datetime.now().isoformat()
    title = f"CHANGE_DONE: {tool_name} → {fname}"
    desc_parts = [f"ファイル: {file_path}", f"ツール: {tool_name}"]
    if lines_after is not None:
        desc_parts.append(f"行数: {lines_after}")
    desc_parts.append(f"timestamp: {now}")
    description = " | ".join(desc_parts)

    payload = json.dumps({
        "title":       title,
        "description": description,
        "tags":        f"auto_hook,{tool_name},post_tool_use",
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
            sent = True
            break
        except Exception as e:
            print(f"[mocka_auto_record] WARN {url}: {e}", flush=True)

    if not sent:
        print(f"[mocka_auto_record] OFFLINE — {fname} (全エンドポイント失敗)", flush=True)

    sys.exit(0)


if __name__ == "__main__":
    main()
