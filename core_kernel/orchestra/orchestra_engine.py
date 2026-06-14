"""
MoCKA Core Kernel — orchestra.orchestra_engine

Orchestra実行層の中核エンジン。
セッション保持・イベント処理・最小ルーティングによるノード実行に加え、
SQLite永続化層への記録(event/execution/output)を行う。
"""

from .event_bus import EventBus
from .execution_graph import ExecutionGraph
from .persistence.sqlite_store import SQLiteStore
from .session_state import SessionState


class OrchestraEngine:
    def __init__(self, store=None):
        self.sessions = {}
        self.graph = ExecutionGraph()
        self.bus = EventBus()

        # 永続化(SQLite Event Store)
        self.store = store if store is not None else SQLiteStore()

    def get_session(self, session_id):
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionState(session_id)
        return self.sessions[session_id]

    def register_node(self, node_id, handler):
        self.graph.add_node(node_id, handler)

    def on_event(self, event):
        session = self.get_session(event.session_id)

        # 1. メモリ記録
        session.apply_event(event)

        # 2. 永続化
        self.store.save_event(event)

        # 3. event bus
        results = self.bus.publish(event)

        # 4. execution
        if "target_node" in event.payload:
            node_id = event.payload["target_node"]

            context = {
                "session_id": session.session_id,
                "event": event,
                "bus_results": results,
            }

            output = self.graph.execute(node_id, context)

            execution_id = f"{event.event_id}:{node_id}"

            session.apply_execution({
                "node_id": node_id,
                "context": context,
                "result": output,
            })

            self.store.save_execution(
                execution_id,
                session.session_id,
                node_id,
                event.timestamp,
                context,
                output,
            )

            self.store.save_output(
                execution_id,
                session.session_id,
                event.timestamp,
                output,
            )

            session.apply_output(output)

            return output

        return results
