"""
MoCKA Core Kernel — orchestra.session_state

セッション単位の状態保持(ノード状態 + イベント履歴)。
"""


class SessionState:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.nodes = {}   # node_id -> state
        self.history = []  # event log

    def update(self, event):
        self.history.append(event)
