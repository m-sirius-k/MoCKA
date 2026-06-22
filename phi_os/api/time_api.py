# phi_os/api/time_api.py
# Phase5 Step1 - Time API v0。MoCKA時間OSの外部参照境界を固定する。
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
