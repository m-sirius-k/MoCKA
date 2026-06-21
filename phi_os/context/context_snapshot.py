"""
Context Runtime v2 — ContextSnapshot
責務: Context全体を定期的にJSONとして保存する。
最新スナップショットは *_latest.json として常に上書き保持する。
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

_SNAP_DIR = Path(__file__).parents[2] / "data" / "context_snapshots"
_MAX_HISTORY = 20
_SCOPED_DIR_NAME = "scoped"


class ContextSnapshot:
    def __init__(self, snap_dir: Path | None = None) -> None:
        self._dir = snap_dir or _SNAP_DIR
        self._dir.mkdir(parents=True, exist_ok=True)

    def save(self, context: dict) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"context_{ts}.json"
        path = self._dir / filename

        payload = {
            "snapshot_version": "v2",
            "saved_at": datetime.now(timezone.utc).isoformat(),
            **context,
        }
        serialized = json.dumps(payload, ensure_ascii=False, indent=2)

        path.write_text(serialized, encoding="utf-8")

        # 最新ポインタを更新
        latest = self._dir / "context_latest.json"
        latest.write_text(serialized, encoding="utf-8")

        # 層別の最新ポインタ
        for layer in ("institution", "working", "memory", "execution"):
            layer_data = context.get(layer)
            if layer_data:
                lpath = self._dir / f"{layer}_context_latest.json"
                lpath.write_text(
                    json.dumps(layer_data, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )

        self._prune()
        return str(path)

    def load_latest(self) -> dict | None:
        latest = self._dir / "context_latest.json"
        if not latest.exists():
            return None
        try:
            return json.loads(latest.read_text(encoding="utf-8"))
        except Exception:
            return None

    def list_snapshots(self) -> list[str]:
        files = sorted(self._dir.glob("context_2*.json"), reverse=True)
        return [str(f) for f in files]

    # ──────────────────────────────────────────
    # H2-2: Actor-scoped Snapshot(3.3) — ハイブリッド方式(博士確定)。
    # snapshot_id/integrity_hash = hash(不可逆・整合性確認のみ)。
    # summary = 構造化要約のみ。raw event chainは一切含めない(再構成不可)。
    # 既存のsave()/load_latest()(global互換)は変更しない。
    # ──────────────────────────────────────────

    def save_scoped(self, actor_id: str, context: dict) -> str:
        """actor-scopedハイブリッドsnapshot保存。audit可能だがreplay不能な形式。"""
        from .access_gate import before_context_update

        before_context_update(actor_id, actor_id)

        working = context.get("working", {})
        memory = context.get("memory", {})

        summary = {
            "current_task": working.get("current_task", ""),
            "current_goal": working.get("current_goal", ""),
            "current_step": working.get("next_action", ""),
            "verification_status": working.get("verification_status", ""),
            "event_count": memory.get("event_count", 0),
        }

        # integrity_hashはraw event chainそのものではなく、その時点のworking/memory
        # 状態のcanonical JSON表現に対するsha256(不可逆・整合性確認専用)。
        canonical = json.dumps(
            {"working": working, "memory": memory}, ensure_ascii=False, sort_keys=True
        )
        integrity_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        snapshot_id = hashlib.sha256(
            f"{actor_id}:{integrity_hash}".encode("utf-8")
        ).hexdigest()[:16]

        payload = {
            "snapshot_id": snapshot_id,
            "actor_id": actor_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": summary,
            "integrity_hash": integrity_hash,
        }

        scoped_dir = self._dir / _SCOPED_DIR_NAME / actor_id
        scoped_dir.mkdir(parents=True, exist_ok=True)
        path = scoped_dir / "snapshot_latest.json"
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return str(path)

    def load_scoped(self, requesting_actor_id: str, target_actor_id: str) -> dict | None:
        """actor-scoped観測(3.3)。自身のactor_id以外を要求した場合は拒否する。"""
        from .access_gate import enforce_observe
        from .permissions import ACTOR_SCOPED

        enforce_observe(requesting_actor_id, target_actor_id, ACTOR_SCOPED)

        path = self._dir / _SCOPED_DIR_NAME / target_actor_id / "snapshot_latest.json"
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _prune(self) -> None:
        files = sorted(self._dir.glob("context_2*.json"), reverse=True)
        for old in files[_MAX_HISTORY:]:
            try:
                old.unlink()
            except Exception:
                pass
