'use strict';
// mocka-bridge.js — MoCKA MCP 送信ブリッジ
// PHI-OS統合時にリアルタイム送信。未接続時は RecordStore にフォールバック。

import { RecordStore } from '../core/change-record-store.js';

const MOCKA_ENDPOINT = 'https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev/mcp';
const CONNECT_TIMEOUT_MS = 3000;

// 接続状態キャッシュ（10秒TTL）
let _connCache     = null;
let _connCacheTime = 0;
const CONN_TTL_MS  = 10000;

async function _checkConnection() {
  if (_connCache !== null && Date.now() - _connCacheTime < CONN_TTL_MS) {
    return _connCache;
  }

  // PHI_OS_ADAPTER が window にある場合は統合モード
  if (typeof globalThis.window !== 'undefined' &&
      typeof globalThis.window.PHI_OS_ADAPTER !== 'undefined') {
    _connCache = true;
    _connCacheTime = Date.now();
    return true;
  }

  // ngrok エンドポイントへの疎通確認
  try {
    const res = await fetch(MOCKA_ENDPOINT, {
      method: 'OPTIONS',
      signal: AbortSignal.timeout(CONNECT_TIMEOUT_MS),
    });
    _connCache = res.status < 500;
  } catch {
    _connCache = false;
  }
  _connCacheTime = Date.now();
  return _connCache;
}

async function _postToMocka(title, description, tags, why_purpose) {
  const body = JSON.stringify({
    method: 'tools/call',
    params: {
      name: 'mocka_write_event',
      arguments: { title, description, tags, why_purpose },
    },
  });

  const res = await fetch(MOCKA_ENDPOINT, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body,
    signal:  AbortSignal.timeout(CONNECT_TIMEOUT_MS),
  });

  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

function _buildTitle(record) {
  const fname = String(record.file).split(/[\\/]/).pop();
  return `${record.type}: ${fname}`;
}

function _buildDescription(record) {
  const parts = [
    `ファイル: ${record.file}`,
    record.reason ? `理由: ${record.reason}` : null,
    record.diff_summary ? `変更内容: ${record.diff_summary}` : null,
    record.lines_before != null ? `変更前行数: ${record.lines_before}` : null,
    record.lines_after  != null ? `変更後行数: ${record.lines_after}` : null,
    record.result ? `結果: ${record.result}` : null,
    `timestamp: ${record.timestamp}`,
  ];
  return parts.filter(Boolean).join(' | ');
}

function _buildTags(record) {
  const ext = String(record.file).match(/\.([a-zA-Z0-9]+)$/)
    ? String(record.file).match(/\.([a-zA-Z0-9]+)$/)[1]
    : 'unknown';
  return `change_tracker,${ext}`;
}

export const MocKABridge = {
  /**
   * MoCKA への接続確認。
   * @returns {Promise<boolean>}
   */
  async isConnected() {
    return _checkConnection();
  },

  /**
   * CHANGE_START レコードを MoCKA へ送信する。
   * @param {object} record
   * @returns {Promise<boolean>} 送信成功なら true
   */
  async sendChangeStart(record) {
    try {
      await _postToMocka(
        _buildTitle(record),
        _buildDescription(record),
        _buildTags(record),
        record.reason || 'change-tracker',
      );
      return true;
    } catch (err) {
      console.warn('[MocKABridge] sendChangeStart failed (fallback to local):', err.message);
      _connCache = false;
      _connCacheTime = Date.now();
      return false;
    }
  },

  /**
   * CHANGE_DONE レコードを MoCKA へ送信する。
   * @param {object} record
   * @returns {Promise<boolean>} 送信成功なら true
   */
  async sendChangeDone(record) {
    try {
      await _postToMocka(
        _buildTitle(record),
        _buildDescription(record),
        _buildTags(record),
        record.reason || 'change-tracker',
      );
      return true;
    } catch (err) {
      console.warn('[MocKABridge] sendChangeDone failed (fallback to local):', err.message);
      _connCache = false;
      _connCacheTime = Date.now();
      return false;
    }
  },

  /**
   * pending（未送信）の全レコードを MoCKA へ送信する。
   * @returns {Promise<{ sent: number, failed: number }>}
   */
  async flushPending() {
    const pending = await RecordStore.getPending();
    let sent = 0, failed = 0;

    for (const record of pending) {
      try {
        await _postToMocka(
          _buildTitle(record),
          _buildDescription(record),
          _buildTags(record),
          record.reason || 'change-tracker',
        );
        await RecordStore.markSynced(record.id);
        sent++;
      } catch {
        failed++;
      }
    }

    if (sent > 0) await RecordStore.updateLastFlush();
    console.log(`[MocKABridge] flush: sent=${sent} failed=${failed}`);
    return { sent, failed };
  },
};
