"""
MoCKA Core Kernel — core_store.persistence_interface

責務:
  永続化の抽象インターフェースのみを定義する。

  - 実ストレージ実装(ファイル/DB等)は行わない。
  - InMemoryBackendは仕様確認・テスト用の最小実装であり、
    本番の永続化先として利用することを意図しない。
"""

from abc import ABC, abstractmethod


class PersistenceBackend(ABC):
    """永続化バックエンドの抽象インターフェース。"""

    @abstractmethod
    def get(self, key: str):
        """keyに対応する値を取得する。存在しない場合はNone。"""
        raise NotImplementedError

    @abstractmethod
    def put(self, key: str, value) -> None:
        """keyに対応する値を保存する。"""
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: str) -> None:
        """keyに対応する値を削除する。存在しない場合は何もしない。"""
        raise NotImplementedError

    @abstractmethod
    def keys(self) -> tuple:
        """保存済みの全keyを返す。"""
        raise NotImplementedError


class InMemoryBackend(PersistenceBackend):
    """テスト/仕様確認用の最小実装(プロセス終了で内容は消える)。"""

    def __init__(self):
        self._data = {}

    def get(self, key: str):
        return self._data.get(key)

    def put(self, key: str, value) -> None:
        self._data[key] = value

    def delete(self, key: str) -> None:
        self._data.pop(key, None)

    def keys(self) -> tuple:
        return tuple(self._data.keys())
