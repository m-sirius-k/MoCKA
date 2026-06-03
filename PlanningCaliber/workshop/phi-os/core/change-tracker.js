'use strict';
// change-tracker.js — 変更追跡コア
// PHI-OS有無に関わらず CHANGE_START / CHANGE_DONE を記録する。

import { RecordStore }  from './change-record-store.js';
import { MocKABridge }  from '../adapters/mocka-bridge.js';

function _makeId() {
  const ts   = Date.now();
  const rand = Math.random().toString(36).slice(2, 6).toUpperCase();
  return `CT_${ts}_${rand}`;
}

function _fileExt(filePath) {
  const m = String(filePath).match(/\.([a-zA-Z0-9]+)$/);
  return m ? m[1].toLowerCase() : 'unknown';
}

// 進行中の CHANGE_START レコードを filePath で管理（CHANGE_DONEで紐付け）
const _pending = new Map();

export const ChangeTracker = {
  /**
   * ファイル変更前に呼ぶ。CHANGE_START レコードを記録する。
   * @param {string} filePath
   * @param {string} reason — 変更理由 (WHY)
   * @param {object} [opts] — { lines_before?: number }
   * @returns {Promise<string>} record.id
   */
  async beforeChange(filePath, reason, opts = {}) {
    const connected = await MocKABridge.isConnected();
    const record = {
      id:               _makeId(),
      type:             'CHANGE_START',
      file:             filePath,
      reason:           reason || '',
      lines_before:     opts.lines_before ?? null,
      lines_after:      null,
      diff_summary:     '',
      result:           null,
      timestamp:        new Date().toISOString(),
      phi_os_connected: connected,
      mocka_synced:     false,
    };

    await RecordStore.append(record);
    _pending.set(filePath, record.id);

    if (connected) {
      const synced = await MocKABridge.sendChangeStart(record);
      if (synced) await RecordStore.markSynced(record.id);
    }

    console.log('[ChangeTracker] CHANGE_START', filePath, record.id);
    return record.id;
  },

  /**
   * ファイル変更後に呼ぶ。CHANGE_DONE レコードを記録する。
   * @param {string} filePath
   * @param {string} result — 'success' | 'fail' | 'partial'
   * @param {object} [opts] — { lines_after?: number, diff_summary?: string }
   * @returns {Promise<string>} record.id
   */
  async afterChange(filePath, result, opts = {}) {
    const connected = await MocKABridge.isConnected();
    const record = {
      id:               _makeId(),
      type:             'CHANGE_DONE',
      file:             filePath,
      reason:           '',
      lines_before:     null,
      lines_after:      opts.lines_after ?? null,
      diff_summary:     opts.diff_summary || '',
      result:           result || 'success',
      timestamp:        new Date().toISOString(),
      phi_os_connected: connected,
      mocka_synced:     false,
    };

    _pending.delete(filePath);
    await RecordStore.append(record);

    if (connected) {
      const synced = await MocKABridge.sendChangeDone(record);
      if (synced) await RecordStore.markSynced(record.id);
    }

    console.log('[ChangeTracker] CHANGE_DONE', filePath, result, record.id);
    return record.id;
  },

  /**
   * ローカルに蓄積された全レコードを返す。
   * @returns {Promise<Array>}
   */
  async getLog() {
    return RecordStore.getAll();
  },

  /**
   * 未送信（mocka_synced: false）のレコードを MoCKA へ送信する。
   * @returns {Promise<{ sent: number, failed: number }>}
   */
  async flush() {
    return MocKABridge.flushPending();
  },
};
