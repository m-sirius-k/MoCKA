"""
essence_resolver.py

Canonical Essence(interface/lever_essence.json)とLegacy Essence Store(旧互換保存領域、
第3ファイル)を読み取り専用で統合するResolver。

DC_20260707_019/020・ESSENCE_CANONICAL_MODEL_PROPOSAL_v0.1.md・
ESSENCE_IMPLEMENTATION_PLAN_v1.0.md準拠。

read-only: 書込み関数は一切持たない。Active Writer(app.pyのauto_update_essence_from_mataka/
_auto_danger_to_essence)・Legacy Writer(essence_classifier.py等)は本モジュールを経由しない。
"""
import json
import sys
import time
import hashlib
from pathlib import Path
from datetime import datetime, timezone

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent))
from event_buffer import get_buffer

CANONICAL_PATH = Path(r"C:\Users\sirok\MoCKA\interface\lever_essence.json")
LEGACY_PATH = Path(r"C:\Users\sirok\planningcaliber\workshop\needle_eye_project\experiments\lever_essence.json")

_FAILURE_LOG_SUPPRESS_SEC = 3600      # canonical取得失敗ログの抑制間隔(1時間に1回まで)
_SUMMARY_LOG_INTERVAL_SEC = 86400     # summaryログの間隔(1日1回)

_state = {
    "last_failure_log_ts": 0.0,
    "last_summary_log_ts": 0.0,
    "canonical_success": 0,
    "canonical_fail": 0,
    "legacy_success": 0,
    "legacy_fail": 0,
    "last_primary_source": None,
}


def _log_event(title, description, tags):
    """
    audit log記録。TODO_347準拠でdb_helper.write_event()の直接呼出は行わず、
    interface/event_buffer.pyのget_buffer().push()経由でGateへ非同期投入する。
    """
    try:
        now = datetime.now(timezone.utc)
        eid = "ESR_" + now.strftime("%Y%m%d_%H%M%S") + "_" + hashlib.sha256(
            (title + description).encode("utf-8")
        ).hexdigest()[:8]
        get_buffer().push({
            "event_id": eid,
            "when": now.isoformat(),
            "who_actor": "essence_resolver",
            "what_type": "essence_resolver_event",
            "where_component": "interface/essence_resolver.py",
            "where_path": "get_display_essence",
            "why_purpose": "Canonical/Legacy Essence取得状況の監査ログ",
            "how_trigger": "auto",
            "channel_type": "internal",
            "lifecycle_phase": "in_operation",
            "risk_level": "normal",
            "title": title,
            "short_summary": description[:200],
            "free_note": tags,
        })
    except Exception:
        pass  # audit logの失敗でResolver本来の読取処理を止めない


def _maybe_log_failure(reason, description):
    now = time.time()
    if now - _state["last_failure_log_ts"] >= _FAILURE_LOG_SUPPRESS_SEC:
        _state["last_failure_log_ts"] = now
        _log_event(
            f"ESSENCE_RESOLVER: Canonical取得失敗({reason})",
            description,
            "essence_resolver,fallback,error",
        )


def _maybe_log_summary():
    now = time.time()
    if now - _state["last_summary_log_ts"] >= _SUMMARY_LOG_INTERVAL_SEC:
        _state["last_summary_log_ts"] = now
        _log_event(
            "ESSENCE_RESOLVER: 日次summary",
            (
                f"canonical_success={_state['canonical_success']} "
                f"canonical_fail={_state['canonical_fail']} "
                f"legacy_success={_state['legacy_success']} "
                f"legacy_fail={_state['legacy_fail']}"
            ),
            "essence_resolver,summary",
        )


def get_canonical_essence() -> dict:
    """
    Canonical Essence(interface/lever_essence.json)を返す。
    read-only。ファイル不在・JSON不正の場合は空dictを返す(例外を上位に投げない)。
    """
    try:
        if not CANONICAL_PATH.exists():
            _state["canonical_fail"] += 1
            _maybe_log_failure("canonical_not_found", f"{CANONICAL_PATH} が存在しません")
            return {}
        data = json.loads(CANONICAL_PATH.read_text(encoding="utf-8"))
        _state["canonical_success"] += 1
        return data
    except json.JSONDecodeError as e:
        _state["canonical_fail"] += 1
        _maybe_log_failure("canonical_json_error", f"{CANONICAL_PATH} のJSON解析に失敗: {e}")
        return {}
    except Exception as e:
        _state["canonical_fail"] += 1
        _maybe_log_failure("canonical_read_error", f"{CANONICAL_PATH} の読取に失敗: {e}")
        return {}


def get_legacy_essence() -> dict:
    """
    Legacy Essence Store(第3ファイル)を返す。
    read-only。ファイル不在・JSON不正の場合は空dictを返す(例外を上位に投げない)。
    """
    try:
        if not LEGACY_PATH.exists():
            _state["legacy_fail"] += 1
            return {}
        data = json.loads(LEGACY_PATH.read_text(encoding="utf-8-sig"))
        _state["legacy_success"] += 1
        return data
    except json.JSONDecodeError:
        _state["legacy_fail"] += 1
        return {}
    except Exception:
        _state["legacy_fail"] += 1
        return {}


def get_display_essence() -> dict:
    """
    COMMAND CENTER/公開API向けの統合ビュー。
    Option2方針(Canonical主表示+Legacy別セクション)に従う。

    戻り値:
        {
            "canonical": dict,            # Canonical Essence(取得失敗時は{})
            "legacy": dict,                # Legacy Essence Store(取得失敗時は{})
            "primary_source": str,         # "canonical" | "legacy" | "none"
            "fallback_reason": str|None,   # fallback発生時の理由、通常時はNone
        }
    """
    canonical = get_canonical_essence()
    legacy = get_legacy_essence()

    if canonical:
        primary_source = "canonical"
        fallback_reason = None
    elif legacy:
        primary_source = "legacy"
        fallback_reason = "canonical_unavailable"
    else:
        primary_source = "none"
        fallback_reason = "both_unavailable"

    if primary_source != "canonical" and _state["last_primary_source"] == "canonical":
        _log_event(
            f"ESSENCE_RESOLVER: primary_sourceがcanonical->{primary_source}へfallback発動",
            f"fallback_reason={fallback_reason}",
            "essence_resolver,fallback",
        )
    _state["last_primary_source"] = primary_source

    _maybe_log_summary()

    return {
        "canonical": canonical,
        "legacy": legacy,
        "primary_source": primary_source,
        "fallback_reason": fallback_reason,
    }


if __name__ == "__main__":
    import pprint
    print("=== get_canonical_essence() ===")
    pprint.pprint(get_canonical_essence())
    print("=== get_legacy_essence() ===")
    pprint.pprint(get_legacy_essence())
    print("=== get_display_essence() ===")
    pprint.pprint(get_display_essence())
