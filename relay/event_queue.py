# relay/event_queue.py
# Relay Phase4 — QUEUE_EVENT判定されたイベントの実体バッファ。
# プロセス内のin-memoryバッファであり、永続化は行わない（プロセス再起動で消える）。
# 永続化が必要な場合はPhase5以降で別途検討する。

class EventQueue:
    def __init__(self):
        self.queue = []

    def push(self, event: dict) -> None:
        self.queue.append(event)

    def pop_all(self) -> list:
        events = self.queue
        self.queue = []
        return events

    def size(self) -> int:
        return len(self.queue)
