# -*- coding: utf-8 -*-
"""
gateway/context_facade.py -- Context Facade (Phase-1.6-Implementation-03)

既存 ContextBuilder と ContextRuntime の境界を吸収する合成層。

    gateway
      |
    ContextFacade
      |
    ContextBuilder / ContextProjection
      |
    ContextRuntime

設計方針:
  - 既存 ContextBuilder を破壊しない。ContextBuilder.build() の完全payloadを
    土台とし、phase / goal のみを ContextRuntime 由来へ差し替える。
  - 既定 mode="shadow" では ContextBuilder の結果をそのまま返す。
    外部仕様(payload schema)も既存consumerの挙動も変更しない。
  - current() に依存しない。runtime_provider 既定は ContextRuntime.boot であり、
    リクエスト毎に最新を取得する(ContextBuilderの鮮度契約と一致させるため)。
    gateway起動時の bind は lifecycle gate であり、本Facadeは参照しない。
  - ContextRuntime の import は既定providerの内部でのみ行う。phi_os が無い環境でも
    本モジュール単体をimport・テストできる。

差し替え面:
  ContextBuilder の消費される公開APIは build(mode) のみ(gateway 4 / connector_caliber 2 /
  connector_router 2 の計9呼出)。本Facadeは build() を実装し、
  ConnectorCaliber(context_builder=...) へ透過的に注入できる。
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

# 比較対象。generated_at / size_bytes / booted_at は呼出毎に変動するため除外する。
COMPARED_FIELDS = ("phase", "goal")

ALLOWED_MODES = ("shadow", "active")

# Shadow比較ログ。.gitignore の logs/context_shadow*.jsonl により
# git status に出さない(GL7のencoding_mismatch走査対象・auto-sync対象から外す)。
_LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "context_shadow.jsonl"
_LOG_MAX_BYTES = 10 * 1024 * 1024


def _default_runtime_provider():
    """
    既定の ContextRuntime 取得経路(HG-15)。

    current() ではなく boot() を使う。ContextBuilder はリクエスト毎に全データ源を
    再読込しており、保持インスタンスを使うとその鮮度契約を後退させるため。
    import を関数内に置き、phi_os 非依存で本モジュールを読み込めるようにする。
    """
    from phi_os.context.context_runtime import ContextRuntime
    return ContextRuntime.boot()


class ContextFacadeError(Exception):
    """Facadeの合成が成立しなかったことを示す。"""


class ContextFacade:
    """
    ContextBuilder 互換の build(mode) を提供する合成層。

    使い方(gateway/gateway.py):
        builder = ContextFacade(ContextBuilder(), ContextProjection())
        connector = ConnectorCaliber(context_builder=builder, ...)
    """

    def __init__(self, builder, projection, mode: str = "shadow",
                 runtime_provider=None) -> None:
        if mode not in ALLOWED_MODES:
            raise ContextFacadeError(
                f"unknown facade mode: {mode!r} (allowed: {','.join(ALLOWED_MODES)})"
            )
        self._builder = builder
        self._projection = projection
        self._mode = mode
        self._runtime_provider = runtime_provider or _default_runtime_provider

    # -- 公開API (ContextBuilder互換) ----

    def build(self, mode: str = "standard", ai_hint: str = None) -> dict:
        """
        shadow: ContextBuilder の結果をそのまま返す。比較のみ記録する。
        active: ContextBuilder の結果に phase / goal を上書きして返す。

        shadow は例外を握り潰す唯一の局面である。既存応答を壊さないため、
        Projection 側の失敗はログへ記録し応答には影響させない。
        active ではこの緩和は失効し、例外は呼出元へ伝播する(fail closed)。
        """
        legacy = self._builder.build(mode, ai_hint)

        if self._mode == "shadow":
            self._record_shadow(legacy, mode)
            return legacy

        projected = self._project(mode)
        return self._merge(legacy, projected)

    @property
    def mode(self) -> str:
        return self._mode

    # -- 内部 ----

    def _project(self, mode: str) -> dict:
        """ContextRuntime を取得し Projection へ通す。例外は捕捉しない。"""
        runtime = self._runtime_provider()
        return self._projection.project(runtime.full_context(), mode)

    def _merge(self, legacy: dict, projected: dict) -> dict:
        """
        legacy payload の phase / goal のみを差し替える。

        size_bytes は ContextBuilder._assemble() と同じ意味論で再計算する
        (size_bytes キーが無い状態の body を計測してから設定する)。
        上書きで文字列長が変われば元の値が実態とずれるため。
        """
        for key in COMPARED_FIELDS:
            if key in projected:
                legacy[key] = projected[key]

        meta = legacy.get("meta")
        if isinstance(meta, dict) and "size_bytes" in meta:
            meta.pop("size_bytes", None)
            size = len(json.dumps(legacy, ensure_ascii=False).encode("utf-8"))
            meta["size_bytes"] = size
        return legacy

    def _record_shadow(self, legacy: dict, mode: str) -> None:
        """
        shadow比較を記録する。応答を壊さないため全例外を捕捉する。
        events.db および connector_caliber._record_event() は使用しない
        (Ledgerへ二重の意味を持つイベントを入れないため)。
        """
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": mode,
            "facade_mode": self._mode,
        }
        try:
            projected = self._project(mode)
            for key in COMPARED_FIELDS:
                entry[f"builder_{key}"] = legacy.get(key, "")
                entry[f"projection_{key}"] = projected.get(key, "")
                entry[f"{key}_match"] = legacy.get(key, "") == projected.get(key, "")
        except Exception as e:
            entry["projection_error"] = f"{type(e).__name__}: {e}"

        try:
            self._append_log(entry)
        except Exception:
            pass

    def _append_log(self, entry: dict) -> None:
        """JSON Lines を UTF-8(BOMなし)で追記する。上限到達時は1世代のみ退避する。"""
        _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        if _LOG_PATH.exists() and _LOG_PATH.stat().st_size >= _LOG_MAX_BYTES:
            _LOG_PATH.replace(_LOG_PATH.with_suffix(".jsonl.1"))
        line = json.dumps(entry, ensure_ascii=False) + "\n"
        with open(_LOG_PATH, "a", encoding="utf-8", newline="\n") as f:
            f.write(line)
