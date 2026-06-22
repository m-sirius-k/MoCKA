# phi_os/semantic/query_resolver.py
# Phase5 Step3 - Semantic Query Layer v1。
#
# 責務は1つだけ: resolve(text) -> query_name (Time Query v0の既存クエリ名) | None
#
# 絶対条件:
#   - LLM/推論は一切使わない。固定キーワードの部分文字列一致のみ。
#   - 未知の入力は推測しない。Noneを返すだけで、呼び出し側がUNRESOLVED_QUERYとして拒否する。
#   - Repository/RelayKernelへは一切アクセスしない。文字列からクエリ名への変換のみを行う。

_KEYWORD_MAP = {
    "イベント数": "event_count",
    "event数": "event_count",
    "event count": "event_count",
    "総イベント数": "event_count",
    "最後のsnapshot": "last_snapshot",
    "最新snapshot": "last_snapshot",
    "snapshot情報": "last_snapshot",
    "現在状態": "current_state",
    "current state": "current_state",
    "状態": "current_state",
    "再構築": "replay_state",
    "replay": "replay_state",
    "再生状態": "replay_state",
    "監査状態": "audit_status",
    "audit": "audit_status",
    "drift": "audit_status",
}

# 長いキーワードを優先してスキャンする(例: 「再生状態」が「状態」を部分文字列として
# 含むため、短い汎用キーワードに先に誤マッチしないようにする)。
_SORTED_KEYWORDS = sorted(_KEYWORD_MAP.items(), key=lambda kv: len(kv[0]), reverse=True)


def resolve(text: str):
    if not text:
        return None

    lowered = text.lower()
    for keyword, query_name in _SORTED_KEYWORDS:
        if keyword.lower() in lowered:
            return query_name

    return None
