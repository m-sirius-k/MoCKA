"""
MoCKA 3.0 — Memory Layer
memory_ingestor.py

責務:
  Orchestra Event Stream(orchestra_events.jsonl)を読み取り、
  「意味単位」のMemoryEntryへ変換してMemory Storeへ書き込む。

  - Event(事実)はそのまま読むだけで変更しない。
  - Memory(意味)は session_id 単位で集約・構造化して生成する。
  - 1 Event = 1 Memory ではない(同一session_idのai_response群を1件に集約)。

  Memory Layerの他モジュール(Store/Registry/Writer)を変更せず、
  既存のwrite_event()を利用して書き込む。
"""

import json
from pathlib import Path

from memory_registry import MemoryType, Source
from memory_store import MemoryStore
from memory_writer import MemoryWriter

ORCHESTRA_EVENTS_PATH = (
    Path(__file__).resolve().parent.parent
    / "caliber" / "orchestra" / "orchestra_events.jsonl"
)


def load_events(events_path: Path = ORCHESTRA_EVENTS_PATH) -> list:
    """orchestra_events.jsonlを読み取り、Event(dict)のリストを返す。

    ファイルが存在しない/空の場合は空リストを返す(エラーにしない)。
    壊れた行は無視する。
    """
    if not events_path.exists():
        return []
    events = []
    with open(events_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def group_by_session(events: list) -> dict:
    """session_idでEventをグルーピングする。session_idの無いEventは無視する。"""
    sessions = {}
    for event in events:
        session_id = event.get("session_id")
        if not session_id:
            continue
        sessions.setdefault(session_id, []).append(event)
    return sessions


def _is_meaningful(event: dict) -> bool:
    """error/timeoutを除外し、意味のある応答のみ採用する(Rule 3-①)。"""
    payload = event.get("payload", {})
    status = event.get("status") or payload.get("status")
    if status in ("error", "timeout"):
        return False
    raw = payload.get("raw") or payload.get("raw_response") or ""
    return bool(raw.strip())


def _extract_ai_responses(events: list) -> list:
    """type=ai_response かつ意味のあるEventのみ抽出する。"""
    return [
        e for e in events
        if e.get("type") == "ai_response" and _is_meaningful(e)
    ]


def _extract_prompt(events: list) -> str:
    """session内のEventから共通promptを抽出する(payload.prompt優先、無ければ空)。"""
    for event in events:
        payload = event.get("payload", {})
        prompt = payload.get("prompt") or event.get("prompt")
        if prompt:
            return prompt
    return ""


def _build_content(prompt: str, ai_responses: list) -> str:
    """Rule B: 構造テンプレに従い、AI応答を統合した意味記憶本文を生成する。

    単純結合ではなく、AIごとの応答を列挙し、共通点/相違点の項目を
    構造として保持する(自動要約器が無いため、項目の有無は後段の
    Retriever/利用者が読み取れる形に整形するに留める)。
    """
    lines = []
    lines.append("[Prompt]")
    lines.append(prompt if prompt else "(prompt不明)")
    lines.append("")
    lines.append("[AI Responses Summary]")
    for event in ai_responses:
        payload = event.get("payload", {})
        ai_name = payload.get("ai_name", "unknown")
        text = payload.get("cleaned_response") or payload.get("raw") or payload.get("raw_response") or ""
        text = text.strip().replace("\n", " ")
        if len(text) > 300:
            text = text[:300] + "..."
        lines.append(f"- {ai_name}: {text}")
    lines.append("")
    lines.append("[Consensus / Difference]")
    lines.append(f"- 参加AI数: {len(ai_responses)}")
    lines.append("- 共通点: (未分析)")
    lines.append("- 相違点: (未分析)")
    return "\n".join(lines)


def _generate_tags(ai_responses: list) -> tuple:
    """Rule: tags = ["orchestra", "multi-ai" or "single-ai", "session", ai_name...]"""
    tags = ["orchestra", "session"]
    tags.append("multi-ai" if len(ai_responses) > 1 else "single-ai")
    for event in ai_responses:
        ai_name = event.get("payload", {}).get("ai_name")
        if ai_name:
            tag = f"ai:{ai_name.lower()}"
            if tag not in tags:
                tags.append(tag)
    return tuple(tags)


def _build_sources(ai_responses: list) -> list:
    """Rule 4: AI別差分を保持するため、raw_responseをsourcesに残す。"""
    sources = []
    for event in ai_responses:
        payload = event.get("payload", {})
        sources.append({
            "ai_name": payload.get("ai_name"),
            "event_id": event.get("id"),
            "raw_response": payload.get("raw") or payload.get("raw_response"),
            "cleaned_response": payload.get("cleaned_response"),
            "page_url": payload.get("page_url"),
        })
    return sources


def ingest_events(events: list, writer: MemoryWriter = None) -> list:
    """Event Streamを意味単位のMemoryEntryへ変換し、Memory Storeへ書き込む。

    Args:
        events: load_events()で得られたEventのリスト
        writer: MemoryWriter(省略時は新規MemoryStoreで作成)

    Returns:
        書き込まれたMemoryEntryのリスト
    """
    writer = writer or MemoryWriter(MemoryStore())
    written = []

    for session_id, session_events in group_by_session(events).items():
        ai_responses = _extract_ai_responses(session_events)
        if not ai_responses:
            # ai_responseが無いsession(session_updateのみ等)は意味記憶化しない
            continue

        prompt = _extract_prompt(session_events)
        content = _build_content(prompt, ai_responses)
        tags = _generate_tags(ai_responses)

        memory_content = {
            "type": "ai_collaboration_summary",
            "session_id": session_id,
            "prompt": prompt,
            "content": content,
            "sources": _build_sources(ai_responses),
        }

        entry = writer.write_event(
            event=memory_content,
            memory_type=MemoryType.EPISODIC,
            source=Source.EXTERNAL,
            tags=tags,
        )
        written.append(entry)

    return written


def main():
    events = load_events()
    entries = ingest_events(events)
    print(f"[memory_ingestor] {len(events)} events -> {len(entries)} memory entries")
    for entry in entries:
        print(f"  - {entry.memory_id} (session={entry.metadata.get('session_id', entry.content.get('session_id'))})")


if __name__ == "__main__":
    main()
