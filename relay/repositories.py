# relay/repositories.py
# Relay Phase5 Step1 - Layer A(構造契約)をコードに固定する境界インターフェース。
#
# これはDB設計ではない。MoCKAの時間構造そのものの境界定義である。
#   Event Log = 事実（immutable）
#   Queue     = 未確定状態（stateful）
#   Snapshot  = 圧縮状態（replaceable）
#
# RelayKernelはこれ以降、具体的なDB実装を知らず、この3つのインターフェースのみに依存する。
# 実装（SQLite/Postgres/in-memory等）はStep2で別ファイルに分離する。

from abc import ABC, abstractmethod


class EventRepository(ABC):
    @abstractmethod
    def append_event(self, event: dict) -> None:
        ...

    @abstractmethod
    def get_events(self, from_id: str = None) -> list:
        ...


class SnapshotRepository(ABC):
    @abstractmethod
    def save_snapshot(self, snapshot: dict) -> None:
        ...

    @abstractmethod
    def load_latest(self) -> dict:
        ...


class QueueRepository(ABC):
    @abstractmethod
    def push(self, event: dict) -> None:
        ...

    @abstractmethod
    def pop(self) -> dict:
        ...

    @abstractmethod
    def update_status(self, queue_id: str, status: str) -> None:
        ...
