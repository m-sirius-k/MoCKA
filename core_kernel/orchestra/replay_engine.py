"""
MoCKA Core Kernel — orchestra.replay_engine

永続化されたイベントからセッションを再構築する(Replay Layer)。
"""

import json

from .persistence.sqlite_store import SQLiteStore


class ReplayEngine:
    def __init__(self, store=None):
        self.store = store if store is not None else SQLiteStore()

    def replay_session(self, session_id):
        events = self.store.load_session_events(session_id)

        reconstructed = []

        for e in events:
            reconstructed.append({
                "event_id": e[0],
                "session_id": e[1],
                "event_type": e[2],
                "timestamp": e[3],
                "payload": json.loads(e[4]),
            })

        return reconstructed
