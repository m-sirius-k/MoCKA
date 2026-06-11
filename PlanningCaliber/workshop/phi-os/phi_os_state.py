"""
PHI-OS Layer1: Stateful Kernel — phi_os_state.py
PHI-OS-SPEC-001 第3章準拠

永続状態（Persistent State）:
  - raw_store     : append-only リスト（削除・変更禁止）  -> raw_store.jsonl
  - semantic_map  : 意味構造dict（追記のみ）              -> semantic_map.json

再構成可能状態（Reconstructable State）:
  - views         : raw_store / semantic_map から再構成可能なキャッシュ
"""
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DATA_ROOT = Path(__file__).parent / "data"
MOCKA_MCP_URL = "http://localhost:5002/agent/mocka_write_event"
REQUEST_TIMEOUT = 5


class StateViolationError(Exception):
    """PHI-OS-SPEC-001 FORBIDDEN② 違反（raw_storeのappend-only制約違反）"""


def _write_mocka_event(title: str, description: str, tags: str, why_purpose: str, author: str) -> None:
    body = json.dumps(
        {
            "title": title,
            "description": description,
            "tags": tags,
            "why_purpose": why_purpose,
            "how_trigger": "phi_os_state.PHIOSState",
            "author": author,
        },
        ensure_ascii=False,
    ).encode("utf-8")
    req = urllib.request.Request(
        MOCKA_MCP_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as res:
            res.read()
    except (urllib.error.URLError, OSError, ValueError):
        # MoCKA未起動でも状態管理自体は継続させる。
        # ただしSTATE_VIOLATION検知時はStateViolationErrorとして別途呼び出し元に伝播する。
        pass


class PHIOSState:
    """
    node_id ごとの永続状態を管理する。

    node_id は生成時に固定。raw_store はファイルへの追記のみで管理し、
    起動のたびに「前回終了時点の件数 <= 現在の件数」をチェックすることで
    append-only制約（FORBIDDEN②）の違反を検知する。
    """

    def __init__(self, node_id: str):
        self._node_id = node_id
        self._dir = DATA_ROOT / node_id
        self._dir.mkdir(parents=True, exist_ok=True)

        self._raw_path = self._dir / "raw_store.jsonl"
        self._semantic_path = self._dir / "semantic_map.json"
        self._meta_path = self._dir / "_meta.json"

        self.raw_store: list = []
        self.semantic_map: dict = {}
        self.views: dict = {}

        self._load()
        self._check_append_only_integrity()

        _write_mocka_event(
            title="PHI_OS_STATE_INIT",
            description=json.dumps(
                {"node_id": self._node_id, "raw_count": len(self.raw_store)},
                ensure_ascii=False,
            ),
            tags="phi_os_state_init",
            why_purpose="PHI-OS起動時の状態初期化（raw_store/semantic_map/viewsロード）",
            author=self._node_id,
        )

    @property
    def node_id(self) -> str:
        return self._node_id

    # ------------------------------------------------------------------
    # 起動時ロード（再起動後の再構成）
    # ------------------------------------------------------------------
    def _load(self) -> None:
        if self._raw_path.exists():
            with open(self._raw_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.raw_store.append(json.loads(line))

        if self._semantic_path.exists():
            self.semantic_map = json.loads(self._semantic_path.read_text(encoding="utf-8"))

        self.views = self._reconstruct_views()

    def _reconstruct_views(self) -> dict:
        """raw_store + semantic_map から views を再構成する（再構成可能状態）。"""
        views: dict = {}
        for rec in self.raw_store:
            source = rec.get("source", "unknown")
            views.setdefault(source, []).append(rec.get("payload"))
        return views

    # ------------------------------------------------------------------
    # append-only違反検知（FORBIDDEN②）
    # ------------------------------------------------------------------
    def _meta(self) -> dict:
        if self._meta_path.exists():
            return json.loads(self._meta_path.read_text(encoding="utf-8"))
        return {}

    def _save_meta(self, raw_count: int) -> None:
        self._meta_path.write_text(
            json.dumps({"raw_count": raw_count}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _check_append_only_integrity(self) -> None:
        meta = self._meta()
        last_count = meta.get("raw_count", 0)
        current_count = len(self.raw_store)

        if current_count < last_count:
            _write_mocka_event(
                title="PHI_OS_ERROR: STATE_VIOLATION",
                description=json.dumps(
                    {
                        "node_id": self._node_id,
                        "error_type": "STATE_VIOLATION",
                        "expected_min": last_count,
                        "actual": current_count,
                        "raw_store_path": str(self._raw_path),
                    },
                    ensure_ascii=False,
                ),
                tags="phi_os_error,state_violation",
                why_purpose="raw_storeのappend-only制約違反検知(PHI-OS-SPEC-001 FORBIDDEN②)",
                author=self._node_id,
            )
            raise StateViolationError(
                f"raw_store append-only違反: 前回記録{last_count}件 -> 現在{current_count}件 "
                f"({self._raw_path})"
            )

        self._save_meta(current_count)

    # ------------------------------------------------------------------
    # raw_store 追記（append-only）
    # ------------------------------------------------------------------
    def append_raw(self, source: str, payload: dict) -> dict:
        # 追記前に「他プロセスによるファイル縮小」がないか再チェックする。
        on_disk_count = 0
        if self._raw_path.exists():
            with open(self._raw_path, encoding="utf-8") as f:
                on_disk_count = sum(1 for line in f if line.strip())
        if on_disk_count < len(self.raw_store):
            _write_mocka_event(
                title="PHI_OS_ERROR: STATE_VIOLATION",
                description=json.dumps(
                    {
                        "node_id": self._node_id,
                        "error_type": "STATE_VIOLATION",
                        "expected_min": len(self.raw_store),
                        "actual": on_disk_count,
                        "raw_store_path": str(self._raw_path),
                    },
                    ensure_ascii=False,
                ),
                tags="phi_os_error,state_violation",
                why_purpose="raw_storeのappend-only制約違反検知(PHI-OS-SPEC-001 FORBIDDEN②)",
                author=self._node_id,
            )
            raise StateViolationError(
                f"raw_store append-only違反: メモリ上{len(self.raw_store)}件 -> "
                f"ディスク上{on_disk_count}件 ({self._raw_path})"
            )

        rec = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "source": source,
            "payload": payload,
        }
        with open(self._raw_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

        self.raw_store.append(rec)

        # semantic_map: 既存キーを上書きせず追記のみ
        self.semantic_map.setdefault(source, []).append(rec["ts"])
        self._semantic_path.write_text(
            json.dumps(self.semantic_map, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        self.views.setdefault(source, []).append(payload)
        self._save_meta(len(self.raw_store))
        return rec

    # ------------------------------------------------------------------
    # views（再構成可能状態）
    # ------------------------------------------------------------------
    def generate_view(self, view_type: str = "fusion") -> dict:
        return {
            "view_type": view_type,
            "node_id": self._node_id,
            "raw_count": len(self.raw_store),
            "sources": {k: list(v) for k, v in self.views.items()},
        }
