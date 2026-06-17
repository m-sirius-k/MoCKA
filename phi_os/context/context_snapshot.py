"""
Context Runtime v2 — ContextSnapshot
責務: Context全体を定期的にJSONとして保存する。
最新スナップショットは *_latest.json として常に上書き保持する。
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

_SNAP_DIR = Path(__file__).parents[2] / "data" / "context_snapshots"
_MAX_HISTORY = 20


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

    def _prune(self) -> None:
        files = sorted(self._dir.glob("context_2*.json"), reverse=True)
        for old in files[_MAX_HISTORY:]:
            try:
                old.unlink()
            except Exception:
                pass
