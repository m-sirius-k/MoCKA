# revision_manager.py
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

from .schema import InstitutionState
from .state_provider import StateProvider
from .state_builder import build_state
from .hash_generator import compute_state_hash


class RevisionStore:
    """revision_store.json の読み書きを担当する。"""

    def __init__(self, store_path: Path):
        self.path = store_path
        self._data = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            with open(self.path, encoding="utf-8") as f:
                return json.load(f)
        return {"revision": 0, "state_hash": ""}

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    @property
    def current_revision(self) -> int:
        return self._data["revision"]

    @property
    def current_hash(self) -> str:
        return self._data["state_hash"]

    def increment(self) -> int:
        self._data["revision"] += 1
        self._save()
        return self._data["revision"]

    def update_hash(self, h: str):
        self._data["state_hash"] = h
        self._save()


def update_institution_state(
    provider: StateProvider,
    store: RevisionStore,
    state_path: Path,
) -> InstitutionState:
    """
    Institution State の更新フロー:
      1. build_state（Pure Function）で State 生成
      2. Hash正規化
      3. 前回 Hash と比較 → 変化があれば Revision++
      4. revision / state_hash / generated_at を付与
      5. current_state.json に保存

    戻り値: 更新後の InstitutionState
    """
    # 1. Pure Function で State 生成
    new_state = build_state(provider)

    # 2. Hash 正規化
    new_hash = compute_state_hash(new_state)

    # 3. 前回 Hash と比較
    if new_hash != store.current_hash:
        new_rev = store.increment()
        store.update_hash(new_hash)
    else:
        new_rev = store.current_revision

    # 4. メタ情報付与
    new_state.revision     = new_rev
    new_state.state_hash   = new_hash
    new_state.generated_at = datetime.now(timezone.utc).isoformat()

    # 5. 保存
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(new_state.to_dict(), f, ensure_ascii=False, indent=2)

    return new_state
