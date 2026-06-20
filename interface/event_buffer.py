#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
event_buffer.py -- Local Event Buffer (TODO_347)
PHI-OS Event Gateを唯一の永続経路としつつ、handshake等の高頻度処理の
レイテンシを守るための非同期バッファ。

push(event)        -- インメモリキューに追加（ブロッキングしない）
flush_async()       -- 1バッチ分をGateの /api/gate/event/batch へ送信
retry_failed()       -- fallback永続化ファイルに残った分を再投入
drain(timeout)       -- shutdown時に可能な限りflushし、残りはfallbackへ永続化

flushは「キューがBATCH_SIZEに達した時」または「FLUSH_INTERVAL秒経過時」の
どちらか早い方で実行される。Gate未応答時はイベントをdata/event_buffer_fallback.jsonl
へ永続化し、次回のflushサイクルで再試行する（exponential backoff）。
"""
import json
import threading
import time
import uuid
import atexit
from pathlib import Path

import requests

GATE_BATCH_URL = "http://localhost:5000/api/gate/event/batch"
FALLBACK_PATH = Path(r"C:\Users\sirok\MoCKA\data\event_buffer_fallback.jsonl")

BATCH_SIZE = 50
FLUSH_INTERVAL_SEC = 0.5      # 仕様: 100ms〜1000ms間隔
MIN_RETRY_INTERVAL_SEC = 5.0
MAX_RETRY_INTERVAL_SEC = 30.0


class EventBuffer:
    def __init__(self):
        self._queue = []
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._retry_interval = MIN_RETRY_INTERVAL_SEC
        self._last_retry_ts = 0.0
        self._load_fallback()
        self._thread = threading.Thread(target=self._run, daemon=True, name="EventBufferFlush")
        self._thread.start()
        atexit.register(self.drain)

    # ── 公開API ──────────────────────────────────────────────
    def push(self, event: dict) -> None:
        """イベントをキューへ追加するのみ。ネットワークI/Oなし＝呼び出し元をブロックしない"""
        ev = dict(event)
        ev.setdefault("idempotency_key", uuid.uuid4().hex)
        ev.setdefault("event_source", "buffered")
        with self._lock:
            self._queue.append(ev)

    def pending_count(self) -> int:
        with self._lock:
            return len(self._queue)

    def flush_async(self) -> int:
        """キュー先頭からBATCH_SIZE件を取り出してGateへ送信する"""
        batch = self._pop_batch(BATCH_SIZE)
        if not batch:
            return 0
        try:
            r = requests.post(GATE_BATCH_URL, json={"events": batch}, timeout=5)
            if r.status_code == 200:
                self._retry_interval = MIN_RETRY_INTERVAL_SEC
                return len(batch)
            print(f"[EventBuffer] batch flush rejected status={r.status_code}: {r.text[:160]}")
            self._persist_fallback(batch)
            return 0
        except requests.exceptions.RequestException as e:
            print(f"[EventBuffer] batch flush失敗(Gate未応答): {e}")
            self._persist_fallback(batch)
            self._retry_interval = min(self._retry_interval * 2, MAX_RETRY_INTERVAL_SEC)
            return 0

    def retry_failed(self) -> None:
        """fallback永続化ファイルの内容をキューへ再投入する"""
        self._load_fallback()

    def drain(self, timeout: float = 5.0) -> None:
        """shutdown時: 可能な限りflushし、残りはfallbackへ永続化して次回起動時に再試行させる"""
        deadline = time.time() + timeout
        while time.time() < deadline and self.pending_count() > 0:
            self.flush_async()
        with self._lock:
            remaining = self._queue
            self._queue = []
        if remaining:
            self._persist_fallback(remaining)
            print(f"[EventBuffer] drain timeout: 残り{len(remaining)}件をfallbackへ永続化")

    # ── 内部実装 ──────────────────────────────────────────────
    def _pop_batch(self, max_n: int):
        with self._lock:
            batch, self._queue = self._queue[:max_n], self._queue[max_n:]
        return batch

    def _load_fallback(self) -> None:
        if not FALLBACK_PATH.exists():
            return
        try:
            lines = FALLBACK_PATH.read_text(encoding="utf-8").splitlines()
        except Exception:
            return
        restored = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                restored.append(json.loads(line))
            except Exception:
                continue
        if restored:
            with self._lock:
                self._queue.extend(restored)
            print(f"[EventBuffer] fallback queueから{len(restored)}件復元")
        try:
            FALLBACK_PATH.unlink()
        except Exception:
            pass

    def _persist_fallback(self, events) -> None:
        if not events:
            return
        try:
            FALLBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(FALLBACK_PATH, "a", encoding="utf-8") as f:
                for ev in events:
                    f.write(json.dumps(ev, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[EventBuffer] fallback永続化失敗: {e}")

    def _run(self) -> None:
        while not self._stop.is_set():
            if self.pending_count() >= BATCH_SIZE:
                self.flush_async()
                continue
            self._stop.wait(FLUSH_INTERVAL_SEC)
            if self.pending_count() > 0:
                self.flush_async()
            now = time.time()
            if now - self._last_retry_ts >= self._retry_interval:
                self._last_retry_ts = now
                self.retry_failed()


_buffer_instance = None
_buffer_lock = threading.Lock()


def get_buffer() -> EventBuffer:
    global _buffer_instance
    with _buffer_lock:
        if _buffer_instance is None:
            _buffer_instance = EventBuffer()
    return _buffer_instance
