"""
MoCKA Core Kernel — orchestra.orchestra_engine

Orchestra実行層の中核エンジン。
セッション保持・イベント処理・最小ルーティングによるノード実行を行う。
"""

from .event_bus import EventBus
from .execution_graph import ExecutionGraph
from .session_state import SessionState


class OrchestraEngine:
    def __init__(self):
        self.sessions = {}
        self.graph = ExecutionGraph()
        self.bus = EventBus()

    def get_session(self, session_id):
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionState(session_id)
        return self.sessions[session_id]

    def register_node(self, node_id, handler):
        self.graph.add_node(node_id, handler)

    def on_event(self, event):
        session = self.get_session(event.session_id)

        # 1. セッション更新
        session.update(event)

        # 2. イベント処理
        results = self.bus.publish(event)

        # 3. ノード実行(最小ルーティング)
        if "target_node" in event.payload:
            node_id = event.payload["target_node"]
            context = {
                "session": session,
                "event": event,
                "bus_results": results,
            }
            output = self.graph.execute(node_id, context)
            return output

        return results
