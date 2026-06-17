"""
PR-OS / MoCKA Bridge
MoCKAイベントシステム ↔ PR-OS の双方向統合レイヤー

統合ポイント:
  MoCKA側                PR-OS側
  ─────────────────────────────────────────────────
  mocka_write_event  →   AI Gate 受付・KS発番
  mocka_add_todo     ←   公開スケジュール登録通知
  mocka_events.db    ←   公開後フィードバック記録
  MoCKA Caliber      →   品質スコア・整合性DB参照
"""
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Optional

try:
    import requests as _requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BRIDGE_LOG = os.path.join(_BASE_DIR, "logs", "mocka_bridge.jsonl")
GATE_RETRY_QUEUE = os.path.join(_BASE_DIR, "data", "gate_retry_queue.jsonl")

# TODO_328: PHI-OS Event Gate経由でMoCKA events.dbへ記録するエンドポイント
# MCPサーバー(5002) → PHI-OS Gate(5000/api/gate/event) → events.db の単一経路
MOCKA_MCP_EVENT_ENDPOINT = "http://localhost:5002/agent/mocka_write_event"


# ── MoCKA SDK ────────────────────────────────────────
def _mocka_available() -> bool:
    """MoCKA MCPツールが利用可能か確認（CLIコンテキスト外では False）"""
    return False   # CLI実行時は直接MoCKA DBを参照

def _log(event_type: str, data: dict):
    """ブリッジログをJSONLに追記"""
    os.makedirs(os.path.dirname(BRIDGE_LOG), exist_ok=True)
    entry = {
        "ts":         datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        **data
    }
    with open(BRIDGE_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _log_gate_failure(ks_id: str, adapter: str, error: str):
    """Gate記録失敗をブリッジログに残す（次回のmocka_get_command_centerで検知可能にする）"""
    _log("gate_failure", {
        "ks_id":   ks_id,
        "adapter": adapter,
        "error":   error,
    })
    print(f"[Bridge] Gate記録失敗(ローカルログ+リトライキュー保存済み): {ks_id} / {adapter} / {error}")


def _enqueue_retry(payload: dict):
    """Gate POST失敗時のpayloadをリトライキューに追記（append-only）"""
    os.makedirs(os.path.dirname(GATE_RETRY_QUEUE), exist_ok=True)
    entry = {
        "retry_id":  f"retry_{int(time.time() * 1000)}",
        "queued_at": datetime.now(timezone.utc).isoformat(),
        "sent":      False,
        "payload":   payload,
    }
    with open(GATE_RETRY_QUEUE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _post_to_gate(payload: dict) -> bool:
    """PHI-OS Event Gate へHTTP POSTする。成功時True、失敗時False。"""
    if not _REQUESTS_AVAILABLE:
        return False
    try:
        resp = _requests.post(MOCKA_MCP_EVENT_ENDPOINT, json=payload, timeout=5)
        resp.raise_for_status()
        return True
    except Exception:
        return False


def retry_pending():
    """
    リトライキュー内の未送信エントリを再送する。
    append-only原則に従い、送信済みエントリは削除せず新行として末尾に積む。
    起動時または定期実行時に呼び出す。
    """
    if not os.path.exists(GATE_RETRY_QUEUE):
        return

    with open(GATE_RETRY_QUEUE, encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    # retry_id単位で最新行を有効とみなす
    latest: dict[str, dict] = {}
    for line in lines:
        try:
            entry = json.loads(line)
            rid = entry.get("retry_id", "")
            if rid:
                latest[rid] = entry
        except json.JSONDecodeError:
            pass

    pending = [e for e in latest.values() if not e.get("sent")]
    if not pending:
        return

    sent_entries = []
    for entry in pending:
        if _post_to_gate(entry["payload"]):
            sent_entries.append({
                "retry_id": entry["retry_id"],
                "queued_at": entry["queued_at"],
                "sent":     True,
                "sent_at":  datetime.now(timezone.utc).isoformat(),
                "payload":  entry["payload"],
            })
            print(f"[Bridge] リトライ送信成功: {entry['retry_id']}")

    if sent_entries:
        with open(GATE_RETRY_QUEUE, "a", encoding="utf-8") as f:
            for e in sent_entries:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")


# ──────────────────────────────────────────────────────
# MoCKA → PR-OS: イベントからKSを生成
# ──────────────────────────────────────────────────────
def ingest_from_event(event: dict) -> Optional[dict]:
    """
    MoCKAイベントをAI Gateに投入してKSを生成する。

    event 形式:
    {
      "id": "EVT_NNN",
      "title": "...",
      "body": "...",
      "tags": [...],
      "category": "...",
      "source": "mocka_write_event"
    }

    Returns: AI Gate処理結果 or None
    """
    from ai_gate.gate import process

    title    = event.get("title", "無題")
    body     = event.get("body", event.get("content", ""))
    tags     = event.get("tags", [])
    category = event.get("category", "")

    if not body.strip():
        _log("skip", {"reason": "empty_body", "event_id": event.get("id")})
        return None

    print(f"[Bridge] MoCKA → AI Gate: {title}")
    result = process(title=title, raw_text=body, tags=tags,
                     category=category, source_type="mocka_event")

    _log("ingest", {
        "mocka_event_id": event.get("id"),
        "ks_id":          result["ks_id"],
        "status":         result["status"],
        "score":          result["score"],
    })
    return result


def ingest_from_file(path: str) -> Optional[dict]:
    """ファイルパスからKSを生成"""
    with open(path, encoding="utf-8") as f:
        content = f.read()
    title = os.path.splitext(os.path.basename(path))[0]
    return ingest_from_event({
        "title":   title,
        "body":    content,
        "source":  "file_import",
        "tags":    [],
        "category": "import"
    })


# ──────────────────────────────────────────────────────
# PR-OS → MoCKA: 公開結果をフィードバック
# ──────────────────────────────────────────────────────
def feedback_publish(ks_id: str, adapter: str,
                     success: bool, url: Optional[str] = None):
    """
    KS公開結果をMoCKAイベントとして記録する。
    ローカルJSONL（後方互換）とPHI-OS Event Gate（events.db永続化）の両方に書き込む。
    Gate到達失敗時はリトライキューに積み、pros.pyには例外を伝播しない。
    """
    status = "published" if success else "failed"

    # 既存処理: ローカルJSONLへの記録（後方互換のため維持）
    _log("feedback_publish", {
        "ks_id":   ks_id,
        "adapter": adapter,
        "status":  status,
        "url":     url,
    })
    print(f"[Bridge] Feedback → MoCKA: {ks_id} / {adapter} / {status}")

    # TODO_328: PHI-OS Event Gate経由でMoCKA events.dbへ永続化
    gate_payload = {
        "title": f"feedback_publish: {adapter} / {ks_id} / {status}",
        "description": (
            f"KS記事({ks_id})の{adapter}への配信結果。"
            f"status={status}" + (f" url={url}" if url else "")
        ),
        "author":      "mocka_bridge_pr_os",  # 必須・空欄不可（TODO_322 Actor強制準拠）
        "why_purpose": "distribution_feedback",
        "how_trigger": "pros_publish",
        "tags":        f"feedback_publish,{adapter},{status}",
    }

    if not _post_to_gate(gate_payload):
        _log_gate_failure(ks_id, adapter,
                          "Gate POST失敗（requestsなし・タイムアウト・接続エラーのいずれか）")
        _enqueue_retry(gate_payload)


def feedback_score(ks_id: str, score: float, corrections: int):
    """AI Gateスコアをブリッジログに記録"""
    _log("feedback_score", {
        "ks_id":       ks_id,
        "score":       score,
        "corrections": corrections,
    })


# ──────────────────────────────────────────────────────
# MoCKAイベントDB直接読み込み（CLIモード）
# ──────────────────────────────────────────────────────
def read_mocka_events(db_path: str, since_id: Optional[str] = None,
                      limit: int = 50) -> list:
    """
    MoCKA events.db (JSON Lines形式) から未処理イベントを読む。
    since_id: このIDより新しいイベントのみ取得
    """
    if not os.path.exists(db_path):
        return []

    events = []
    with open(db_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
                events.append(ev)
            except json.JSONDecodeError:
                continue

    # since_id フィルタ
    if since_id:
        ids = [e.get("id") for e in events]
        if since_id in ids:
            idx = ids.index(since_id)
            events = events[idx+1:]

    return events[-limit:]


def sync_from_mocka(db_path: str, auto_confirm: bool = True) -> dict:
    """
    MoCKAイベントDBを走査し、未処理のものをAI Gateに投入する。
    Returns: {"processed": int, "confirmed": int, "pending": int, "errors": int}
    """
    # ブリッジログから最後に処理したIDを取得
    last_id = _get_last_processed_id()
    events  = read_mocka_events(db_path, since_id=last_id)

    if not events:
        print("[Bridge] 新規イベントなし")
        return {"processed": 0, "confirmed": 0, "pending": 0, "errors": 0}

    stats = {"processed": 0, "confirmed": 0, "pending": 0, "errors": 0}
    for ev in events:
        try:
            result = ingest_from_event(ev)
            if result:
                stats["processed"] += 1
                if result["status"] == "confirmed":
                    stats["confirmed"] += 1
                else:
                    stats["pending"] += 1
        except Exception as e:
            stats["errors"] += 1
            _log("error", {"event_id": ev.get("id"), "error": str(e)})

    print(f"[Bridge] 同期完了: {stats}")
    return stats


def _get_last_processed_id() -> Optional[str]:
    """ブリッジログから最後に処理したMoCKAイベントIDを取得"""
    if not os.path.exists(BRIDGE_LOG):
        return None
    last = None
    with open(BRIDGE_LOG, encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("event_type") == "ingest":
                    last = entry.get("mocka_event_id")
            except Exception:
                pass
    return last


# ──────────────────────────────────────────────────────
# Bridge Status
# ──────────────────────────────────────────────────────
def status() -> dict:
    """ブリッジの状態サマリーを返す"""
    log_entries = []
    if os.path.exists(BRIDGE_LOG):
        with open(BRIDGE_LOG, encoding="utf-8") as f:
            for line in f:
                try:
                    log_entries.append(json.loads(line.strip()))
                except Exception:
                    pass

    ingests      = [e for e in log_entries if e.get("event_type") == "ingest"]
    feedbacks    = [e for e in log_entries if e.get("event_type") == "feedback_publish"]
    gate_failures = [e for e in log_entries if e.get("event_type") == "gate_failure"]
    errors       = [e for e in log_entries if e.get("event_type") == "error"]

    retry_pending_count = 0
    if os.path.exists(GATE_RETRY_QUEUE):
        latest: dict = {}
        with open(GATE_RETRY_QUEUE, encoding="utf-8") as f:
            for line in f:
                try:
                    e = json.loads(line.strip())
                    rid = e.get("retry_id", "")
                    if rid:
                        latest[rid] = e
                except Exception:
                    pass
        retry_pending_count = sum(1 for e in latest.values() if not e.get("sent"))

    return {
        "log_entries":         len(log_entries),
        "total_ingested":      len(ingests),
        "total_feedbacks":     len(feedbacks),
        "total_gate_failures": len(gate_failures),
        "total_errors":        len(errors),
        "retry_pending":       retry_pending_count,
        "last_ingest":         ingests[-1]["ts"] if ingests else None,
        "last_feedback":       feedbacks[-1]["ts"] if feedbacks else None,
        "last_processed_id":   _get_last_processed_id(),
    }


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        cmd = sys.argv[1]
        if cmd == "status":
            print(json.dumps(status(), ensure_ascii=False, indent=2))
        elif cmd == "sync" and len(sys.argv) >= 3:
            result = sync_from_mocka(sys.argv[2])
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif cmd == "ingest-file" and len(sys.argv) >= 3:
            result = ingest_from_file(sys.argv[2])
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif cmd == "retry":
            retry_pending()
            print("[Bridge] リトライ処理完了")
        else:
            print(f"未知のコマンド: {cmd}")
    else:
        print("Usage:")
        print("  python mocka_bridge.py status")
        print("  python mocka_bridge.py sync <mocka_events.db>")
        print("  python mocka_bridge.py ingest-file <file.md>")
        print("  python mocka_bridge.py retry")
