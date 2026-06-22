# phi_os/api/time_api.py
# Phase5 Step1 - Time API v0。MoCKA時間OSの外部参照境界を固定する。
# Phase5 Step2 - Time Query Layer v0。/time/queryで固定コマンド方式の問い合わせを提供する。
#   自然言語解析・LLM解釈・GPT連携・MCP接続は一切行わない(これは「問い合わせモデルを固定する段階」)。
# Phase5 Step2.5 - Time Capability Layer。/time/capabilitiesで問い合わせ可能な能力を自己記述する。
#   これはSemantic Query Layer(将来のStep3)の前提契約であり、自然言語解析は一切実装しない。
# Phase5 Step3 - Semantic Query Layer v1。/time/semantic_queryで自然言語(固定キーワード)を
#   既存の/time/query契約へ変換する。LLM/推論は使わず、未解決の入力はUNRESOLVED_QUERYで拒否する。
#   query_resolver.resolve()はテキストからクエリ名への変換のみを行い、Repository/RelayKernelには
#   一切アクセスしない。実行は必ず既存の_QUERY_HANDLERS(Step2契約)経由で行う。
#
# 絶対条件:
#   - 読み取り専用(/time/replayはRelayKernel.replay()の実行のみで、状態破壊・モード変更は行わない)
#   - localhost(127.0.0.1)限定
#   - RelayKernelを唯一の入口とする(ReplayEngine/ReplayRouter/Repositoryへ直接アクセスしない)
#   - ReplayMode変更API/Queue更新API/Snapshot生成API/Event追加APIは実装しない
#
# RelayKernel/ReplayEngine/ReplayRouter/Repository系の既存クラスへの変更は一切行わない。
# 本ファイルはそれらを「呼ぶだけ」の境界層である。

from flask import Blueprint, jsonify, request

from relay.relay_kernel import RelayKernel
from phi_os.semantic.query_resolver import resolve as resolve_semantic_query

time_api_bp = Blueprint("time_api", __name__)

# Time API唯一のRelayKernelシングルトン。他のAPIエンドポイントもこのインスタンスのみを参照する。
_kernel = RelayKernel()

_ALLOWED_HOSTS = {"127.0.0.1", "::1", "localhost"}


@time_api_bp.before_request
def _restrict_to_localhost():
    if request.remote_addr not in _ALLOWED_HOSTS:
        return jsonify({"ok": False, "error": "localhost only"}), 403


@time_api_bp.route("/time/state", methods=["GET"])
def get_state():
    return jsonify({"ok": True, "state": _kernel.state}), 200


@time_api_bp.route("/time/events", methods=["GET"])
def get_events():
    limit = request.args.get("limit", type=int)
    offset = request.args.get("offset", type=int, default=0)

    events = _kernel.event_repository.get_events()
    sliced = events[offset:offset + limit] if limit is not None else events[offset:]

    return jsonify({"ok": True, "count": len(events), "events": sliced}), 200


@time_api_bp.route("/time/replay", methods=["POST"])
def post_replay():
    # modeフィールドは記録目的のみ。ReplayModeの変更は行わない(現在のreplay_router.modeで実行する)。
    request.get_json(silent=True)
    result = _kernel.replay()
    return jsonify({"ok": True, "state": result["final_state"]}), 200


@time_api_bp.route("/time/audit", methods=["GET"])
def get_audit():
    limit = request.args.get("limit", type=int, default=10)
    entries = _kernel.replay_audit_log.get_recent(limit=limit)
    return jsonify({"ok": True, "entries": entries}), 200


def _query_event_count() -> dict:
    return {"ok": True, "event_count": _kernel.state.get("event_count", 0)}


def _query_last_snapshot() -> dict:
    snapshot = _kernel.snapshot_repository.load_latest()
    if snapshot is None:
        return {"ok": True, "snapshot_id": None, "created_at": None}
    return {
        "ok": True,
        "snapshot_id": snapshot["snapshot_id"],
        "created_at": snapshot["timestamp"],
    }


def _query_current_state() -> dict:
    return {"ok": True, "state": _kernel.state}


def _query_replay_state() -> dict:
    result = _kernel.replay()
    return {"ok": True, "state": result["final_state"]}


def _query_audit_status() -> dict:
    entries = _kernel.replay_audit_log.get_recent(limit=50)
    last_match = entries[0]["match"] if entries else None
    drift_count = sum(1 for e in entries if not e["match"])
    return {"ok": True, "last_match": last_match, "drift_count": drift_count}


_QUERY_HANDLERS = {
    "event_count": _query_event_count,
    "last_snapshot": _query_last_snapshot,
    "current_state": _query_current_state,
    "replay_state": _query_replay_state,
    "audit_status": _query_audit_status,
}

# 能力カタログ(機械可読メタデータ)。Semantic Query Layerはこのカタログを参照して
# 自然言語をクエリ名にマッピングする(本ファイルではマッピング処理自体は実装しない)。
_QUERY_CAPABILITIES = {
    "event_count": "total number of events recorded in EventRepository",
    "last_snapshot": "the most recent snapshot id and its creation timestamp",
    "current_state": "the kernel's current in-memory state",
    "replay_state": "the reconstructed state from running RelayKernel.replay()",
    "audit_status": "the most recent replay audit match result and drift count",
}


@time_api_bp.route("/time/query", methods=["POST"])
def post_query():
    body = request.get_json(silent=True) or {}
    query = body.get("query")

    handler = _QUERY_HANDLERS.get(query)
    if handler is None:
        return jsonify({"ok": False, "error": "unknown query"}), 400

    return jsonify(handler()), 200


@time_api_bp.route("/time/capabilities", methods=["GET"])
def get_capabilities():
    capabilities = [
        {"name": name, "description": _QUERY_CAPABILITIES[name]}
        for name in _QUERY_HANDLERS
    ]
    return jsonify({"ok": True, "capabilities": capabilities}), 200


@time_api_bp.route("/time/semantic_query", methods=["POST"])
def post_semantic_query():
    body = request.get_json(silent=True) or {}
    text = body.get("query")

    query_name = resolve_semantic_query(text)
    handler = _QUERY_HANDLERS.get(query_name)
    if handler is None:
        return jsonify({"ok": False, "error": "UNRESOLVED_QUERY"}), 400

    return jsonify(handler()), 200
