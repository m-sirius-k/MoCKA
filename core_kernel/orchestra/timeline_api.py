"""
MoCKA Core Kernel — orchestra.timeline_api

Memory OS View(Timeline API)。永続化されたセッションの全イベントを返す。
"""

from .replay_engine import ReplayEngine

replay = ReplayEngine()


def get_full_session(session_id):
    return replay.replay_session(session_id)
