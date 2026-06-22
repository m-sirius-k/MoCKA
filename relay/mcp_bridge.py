# relay/mcp_bridge.py
# MCP Layer と Event Integrity Framework v1.0 を繋ぐ唯一の橋。
# MCP経由の外部イベント(GitHub/filesystem/http)は意思決定ではなく観測データ
# (operational telemetry)であるため、AI主体governance writeの厳格検証(validate())
# を要求するprocess_event()ではなく、phi_os.event_gate.process_buffered_event()
# (validate_operational()による軽量検証)を経由する。

from mcp.mcp_gateway import MCPGateway
from phi_os.event_gate import process_buffered_event, _get_conn, _ensure_idempotency_table
from relay.relay_kernel import RelayKernel


class MCPBridge:
    def __init__(self):
        self.gateway = MCPGateway()
        self.kernel = RelayKernel()

    def handle(self, source: str, payload: dict) -> dict:
        normalized = self.gateway.ingest(source, payload)

        # Relay Kernel: in-memory state/history蓄積+policy評価+action決定。DB永続化はしない。
        kernel_result = self.kernel.ingest(normalized)
        action = kernel_result["action"]

        # ActionRouterの決定に基づき、ここがDB書き込みの唯一の実行点となる。
        # QUEUE_EVENT: 実際のキュー機構は未実装(Phase4以降の課題)のため、現状は
        # DB書き込みをスキップするのみで実イベントは保持されない。
        if action["action"] == "STORE_EVENT":
            operational_event = {
                "what_type": normalized["type"],
                "where_component": "mcp",
                "why_purpose": f"MCP ingestion from source={source}",
                "who_actor": "mcp_bridge",
                "raw": normalized,
            }

            conn = _get_conn()
            try:
                _ensure_idempotency_table(conn)
                result = process_buffered_event(operational_event, conn)
                conn.commit()
            finally:
                conn.close()
        else:
            result = {"status": "skipped"}

        result["relay_state"] = kernel_result["state"]
        result["policy"] = kernel_result["policy"]
        result["action"] = action
        return result
