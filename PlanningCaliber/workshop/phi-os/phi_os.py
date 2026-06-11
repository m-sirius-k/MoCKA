"""
PHI-OS Hub — phi_os.py
PHI-OS_Core_Spec_v1.0_addendum.md TODO_298 / TODO_299 実装

TODO_298: ingest() -> mocka_write_event 接続
TODO_299: vasAI 双方向ループ実装
"""
import json
import urllib.request
import urllib.error

MOCKA_MCP_URL = "http://localhost:5002/agent/mocka_write_event"
VASAI_FEEDBACK_URL = "http://localhost:6000/phios/feedback"
MAX_LOOP_COUNT = 3
REQUEST_TIMEOUT = 5


class PHIOSError(Exception):
    """PHI-OS の規約違反・致命的エラー"""


class PHIOS:
    """
    PHI-OS Hub。

    node_id 命名規則: phi-os-{layer}-{product}-{instance}
    例:
      phi-os-mocka-core-001
      phi-os-vasai-core-001
      phi-os-mini-orchestra-001
    """

    def __init__(self, layer: str, product: str, instance: str = "001"):
        self.node_id = f"phi-os-{layer}-{product}-{instance}"

    # ------------------------------------------------------------------
    # TODO_298: ingest() -> mocka_write_event 接続
    # ------------------------------------------------------------------
    def ingest(self, source: str, payload: dict) -> dict:
        """
        外部ソースからのデータを取り込み、必ず mocka_write_event に記録する。

        記録なしの ingest() は FORBIDDEN。
        記録に失敗した場合は PHIOSError を送出し、呼び出し元に処理中断を返す。
        """
        description = json.dumps(
            {"source": source, "payload": payload}, ensure_ascii=False
        )
        try:
            self._write_event(
                title=f"PHI_OS_INGEST: {source}",
                description=description,
                tags="phi_os_ingest",
                why_purpose=f"PHI-OS ingest({source})",
                how_trigger=f"{self.node_id}.ingest",
            )
        except Exception as e:
            self._handle_error("INGEST_FAIL", {"source": source, "error": str(e)})
            raise PHIOSError(
                f"ingest({source}) は記録に失敗したため FORBIDDEN: {e}"
            ) from e

        return {"node_id": self.node_id, "source": source, "recorded": True}

    # ------------------------------------------------------------------
    # 4章 / 5.2: generate_view('fusion')
    # ------------------------------------------------------------------
    def generate_view(self, view_type: str, payload: dict) -> dict:
        """
        再投入用のviewを生成する。

        5.2準拠: 再投入後の view_type は常に 'fusion' 固定。
        """
        view = dict(payload)
        view["view_type"] = view_type
        view["node_id"] = self.node_id
        return view

    # ------------------------------------------------------------------
    # TODO_299: vasAI 双方向ループ実装
    # ------------------------------------------------------------------
    def sync(self, target: str, payload: dict) -> dict:
        """
        target との同期を行う。target == 'vasai' の場合は bidirectional 強制。

        ループ終了条件:
          - feedback.status == 'STABLE' -> 再投入しない
          - 再投入回数が MAX_LOOP_COUNT(3) を超過 -> LOOP_LIMIT_REACHED を記録して停止
          - mocka から HALT 命令を受信 -> 即時停止
        """
        if target != "vasai":
            raise PHIOSError(f"sync() は 'vasai' のみ対応（target={target!r}）")

        return self._sync_vasai_bidirectional(payload)

    def _sync_vasai_bidirectional(self, payload: dict) -> dict:
        view = dict(payload)
        view["view_type"] = "fusion"
        loop_count = 0

        while True:
            feedback = self._call_vasai(view)

            if feedback.get("halt"):
                self._write_event(
                    title="PHI_OS_VASAI_HALT",
                    description=json.dumps(
                        {"feedback": feedback, "loop_count": loop_count},
                        ensure_ascii=False,
                    ),
                    tags="phi_os_sync,vasai,halt",
                    why_purpose="mockaからのHALT命令受信のためvasAI同期を即時停止",
                    how_trigger=f"{self.node_id}.sync(vasai)",
                )
                return {"status": "HALTED", "loop_count": loop_count, "feedback": feedback}

            if feedback.get("status") == "STABLE":
                return {"status": "STABLE", "loop_count": loop_count, "feedback": feedback}

            loop_count += 1
            if loop_count > MAX_LOOP_COUNT:
                self._handle_error(
                    "LOOP_LIMIT",
                    {"loop_count": loop_count, "feedback": feedback},
                )
                self._write_event(
                    title="PHI_OS_VASAI_LOOP_LIMIT_REACHED",
                    description=json.dumps(
                        {"feedback": feedback, "loop_count": loop_count},
                        ensure_ascii=False,
                    ),
                    tags="phi_os_sync,vasai,loop_limit",
                    why_purpose=f"MAX_LOOP_COUNT({MAX_LOOP_COUNT})を超過したため停止",
                    how_trigger=f"{self.node_id}.sync(vasai)",
                )
                return {
                    "status": "LOOP_LIMIT_REACHED",
                    "loop_count": loop_count,
                    "feedback": feedback,
                }

            # 再投入: 元のdecision情報を保持しつつfeedbackを反映する。
            # view_type は常に 'fusion' 固定。
            merged = dict(payload)
            merged.update(feedback)
            view = self.generate_view("fusion", merged)

    def _call_vasai(self, view: dict) -> dict:
        view_with_node = dict(view)
        view_with_node["node_id"] = self.node_id
        body = json.dumps(view_with_node, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            VASAI_FEEDBACK_URL,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as res:
                return json.loads(res.read().decode("utf-8"))
        except (urllib.error.URLError, OSError, ValueError) as e:
            self._handle_error("SYNC_FAIL", {"error": str(e), "view": view_with_node})
            raise PHIOSError(f"vasAI同期に失敗: {e}") from e

    # ------------------------------------------------------------------
    # 改善⑤: エラー記録仕様
    # ------------------------------------------------------------------
    def _handle_error(self, error_type: str, context: dict) -> None:
        """
        error_type: LOOP_LIMIT / DIRECTION_VIOLATION / SYNC_FAIL / INGEST_FAIL
        """
        self._write_event(
            title=f"PHI_OS_ERROR: {error_type}",
            description=json.dumps(context, ensure_ascii=False),
            tags=f"phi_os_error,{error_type.lower()}",
            why_purpose=f"PHI-OS エラー記録（{error_type}）",
            how_trigger=f"{self.node_id}._handle_error",
        )

    def assert_vasai_direction(self, condition: bool, message: str) -> None:
        """
        vasAI方向違反のassert。違反時は DIRECTION_VIOLATION を記録し例外を送出する。
        """
        if not condition:
            self._handle_error("DIRECTION_VIOLATION", {"message": message})
            raise PHIOSError(f"DIRECTION_VIOLATION: {message}")

    # ------------------------------------------------------------------
    # mocka_write_event 送信（MoCKA未起動時も処理は継続させない=FORBIDDEN）
    # ------------------------------------------------------------------
    def _write_event(
        self,
        title: str,
        description: str,
        tags: str,
        why_purpose: str,
        how_trigger: str,
    ) -> dict:
        body = json.dumps(
            {
                "title": title,
                "description": description,
                "tags": tags,
                "why_purpose": why_purpose,
                "how_trigger": how_trigger,
                "author": self.node_id,
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
                return json.loads(res.read().decode("utf-8"))
        except (urllib.error.URLError, OSError, ValueError) as e:
            raise PHIOSError(f"MoCKAへのevent記録に失敗: {e}") from e
