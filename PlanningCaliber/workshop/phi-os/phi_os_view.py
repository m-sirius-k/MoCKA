"""
PHI-OS Layer3: View Engine — phi_os_view.py
PHI-OS-SPEC-001 第6章準拠

4視点:
  default  : semantic_mapの標準出力（mockaへの定期レポート用）
  risk     : high_density検知（同一keyへの書き込み頻度 > 閾値）（TIC連携用）
  fusion   : 複数ソースの意味マージ＋差異抽出（vasAIループ制御用）
  timeline : raw_store全件の時系列整列（監査・インシデント解析用）

共通仕様:
  - generate()呼び出し時に mocka_write_event(PHI_OS_VIEW) 発火
  - view_type不明の場合 mocka_write_event(PHI_OS_ERROR, error_type=UNKNOWN_VIEW_TYPE)
  - キャッシュはraw_store更新時に自動invalidate
"""
import json

from phi_os_state import PHIOSState, _write_mocka_event

VIEW_TYPES = ("default", "risk", "fusion", "timeline")
HIGH_DENSITY_THRESHOLD = 10


class ViewError(Exception):
    """view_typeが不明な場合などのView Engineエラー"""


class ViewEngine:
    def __init__(self, state: PHIOSState):
        self._state = state
        self._cache: dict = {}
        self._cache_raw_count = -1

    # ------------------------------------------------------------------
    # キャッシュ管理（raw_store更新時に自動invalidate）
    # ------------------------------------------------------------------
    def _invalidate_if_stale(self) -> None:
        current = len(self._state.raw_store)
        if current != self._cache_raw_count:
            self._cache = {}
            self._cache_raw_count = current

    # ------------------------------------------------------------------
    # 視点生成
    # ------------------------------------------------------------------
    def generate(self, view_type: str, payload: dict = None) -> dict:
        payload = payload or {}
        self._invalidate_if_stale()

        if view_type not in VIEW_TYPES:
            _write_mocka_event(
                title="PHI_OS_ERROR: UNKNOWN_VIEW_TYPE",
                description=json.dumps(
                    {"node_id": self._state.node_id, "view_type": view_type,
                     "error_type": "UNKNOWN_VIEW_TYPE"},
                    ensure_ascii=False,
                ),
                tags="phi_os_error,unknown_view_type",
                why_purpose="不明なview_typeでのgenerate_view呼び出し検知",
                author=self._state.node_id,
            )
            raise ViewError(f"unknown view_type: {view_type!r} (valid: {VIEW_TYPES})")

        if view_type not in self._cache:
            builder = getattr(self, f"_build_{view_type}")
            self._cache[view_type] = builder()

        view = dict(self._cache[view_type])
        view.update(payload)
        view["view_type"] = view_type
        view["node_id"] = self._state.node_id

        _write_mocka_event(
            title=f"PHI_OS_VIEW: {view_type}",
            description=json.dumps(
                {"node_id": self._state.node_id, "view_type": view_type,
                 "raw_count": len(self._state.raw_store)},
                ensure_ascii=False,
            ),
            tags=f"phi_os_view,{view_type}",
            why_purpose=f"PHI-OS view生成({view_type})",
            author=self._state.node_id,
        )
        return view

    # ------------------------------------------------------------------
    # default: semantic_mapの標準出力
    # ------------------------------------------------------------------
    def _build_default(self) -> dict:
        return {"semantic_map": dict(self._state.semantic_map)}

    # ------------------------------------------------------------------
    # risk: high_density検知（同一keyへの書き込み頻度 > 閾値）
    # ------------------------------------------------------------------
    def _build_risk(self) -> dict:
        density = {key: len(entries) for key, entries in self._state.semantic_map.items()}
        high_density = [key for key, count in density.items() if count > HIGH_DENSITY_THRESHOLD]
        return {
            "density": density,
            "high_density": high_density,
            "threshold": HIGH_DENSITY_THRESHOLD,
        }

    # ------------------------------------------------------------------
    # fusion: 複数ソースの意味マージ＋差異抽出
    # ------------------------------------------------------------------
    def _build_fusion(self) -> dict:
        merged: dict = {}
        diffs: dict = {}

        for source, payloads in self._state.views.items():
            for item in payloads:
                if not isinstance(item, dict):
                    continue
                for key, value in item.items():
                    if key in merged and merged[key] != value:
                        diffs.setdefault(key, []).append({"source": source, "value": value})
                    else:
                        merged[key] = value

        return {"merged": merged, "diffs": diffs}

    # ------------------------------------------------------------------
    # timeline: raw_store全件の時系列整列
    # ------------------------------------------------------------------
    def _build_timeline(self) -> dict:
        events = sorted(self._state.raw_store, key=lambda rec: rec["ts"])
        return {"events": events}
