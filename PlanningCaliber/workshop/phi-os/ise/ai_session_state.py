# ai_session_state.py
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class AISessionEntry:
    ai_id:         str
    last_revision: int
    role:          str
    trust_level:   str
    last_knock:    str = ""

class AISessionStore:
    """
    ai_session_state.json の読み書きを担当する。
    Institution State の revision とは完全独立。
    GPT の revision 更新は Institution State の Revision に影響しない。
    """

    def __init__(self, path: Path):
        self.path = path
        self._data: dict[str, AISessionEntry] = self._load()

    def _load(self) -> dict[str, AISessionEntry]:
        if not self.path.exists():
            return {}
        with open(self.path, encoding="utf-8") as f:
            raw = json.load(f).get("ai_registry", {})
        return {
            k: AISessionEntry(ai_id=k, **v)
            for k, v in raw.items()
        }

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        out = {"ai_registry": {
            k: {f: getattr(v, f) for f in
                ["last_revision","role","trust_level","last_knock"]}
            for k, v in self._data.items()
        }}
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)

    def get(self, ai_id: str) -> AISessionEntry | None:
        return self._data.get(ai_id)

    def upsert(self, entry: AISessionEntry):
        self._data[entry.ai_id] = entry
        self._save()

    def update_knock(self, ai_id: str, applied_revision: int):
        entry = self._data.get(ai_id)
        if entry:
            entry.last_revision = applied_revision
            entry.last_knock = datetime.now(timezone.utc).isoformat()
            self._save()

    def all(self) -> dict[str, AISessionEntry]:
        return dict(self._data)

    def register_new(self, ai_id: str, role: str,
                     trust_level: str = "trial") -> AISessionEntry:
        entry = AISessionEntry(
            ai_id         = ai_id,
            last_revision = 0,
            role          = role,
            trust_level   = trust_level,
            last_knock    = "",
        )
        self.upsert(entry)
        return entry
