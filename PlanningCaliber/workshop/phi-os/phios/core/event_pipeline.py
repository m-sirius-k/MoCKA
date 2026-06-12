# phi_os/core/event_pipeline.py
"""
EventPipeline — emit_eventの単一経路。

validate -> enrich -> persist -> audit の4段で構成される。
emit_eventを直接呼ぶ箇所は state_builder.py のみとし、
それ以外のモジュールは pipeline.emit() を経由すること。
"""
from __future__ import annotations

from ise import decision_ledger
from phios.registry.taxonomy import validate_event_type, get_category, is_revision_update, get_taxonomy


class EventPipeline:
    def emit(self, event_type: str, **kwargs) -> dict:
        entry = self._validate(event_type, kwargs)
        entry = self._enrich(entry)
        self._persist(entry)
        self._audit(entry)
        return entry

    # ── validate ──────────────────────────────────────────────
    def _validate(self, event_type: str, kwargs: dict) -> dict:
        if not validate_event_type(event_type):
            raise ValueError(f"Unknown event_type: '{event_type}'. Must be defined in taxonomy v1.1")
        return {"event_type": event_type, **kwargs}

    # ── enrich ────────────────────────────────────────────────
    def _enrich(self, entry: dict) -> dict:
        event_type = entry["event_type"]
        entry["category"] = get_category(event_type)
        entry["revision_increment"] = is_revision_update(event_type)
        entry["severity"] = self._severity_of(event_type, entry["category"])
        return entry

    def _severity_of(self, event_type: str, category: str | None) -> str:
        if category is None:
            return "info"
        taxonomy = get_taxonomy()
        definition = taxonomy.get("events", {}).get(category, {}).get(event_type, {})
        return definition.get("severity", "info")

    # ── persist ───────────────────────────────────────────────
    def _persist(self, entry: dict) -> None:
        category = entry.get("category")
        if category in decision_ledger.ALLOWED_DECISION_CATEGORIES:
            decision_ledger.append_decision(
                decision_type=entry["event_type"],
                actor=entry.get("actor", "system"),
                before=entry.get("before", ""),
                after=entry.get("after", ""),
                reason=entry.get("reason", ""),
                prev_hash=entry.get("prev_hash", ""),
            )

    # ── audit ─────────────────────────────────────────────────
    def _audit(self, entry: dict) -> None:
        if entry.get("severity") == "critical":
            try:
                self._audit_hook(entry)
            except Exception:
                # auditフックの失敗はemit()全体を止めない
                pass

    def _audit_hook(self, entry: dict) -> None:
        """CRITICAL severityイベントの追加監査処理（拡張ポイント）"""
        pass


pipeline = EventPipeline()
