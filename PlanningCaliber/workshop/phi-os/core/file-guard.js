'use strict';
// file-guard.js — ファイル操作ガード（TODO_153 主力）
// create_file / present_files 完了直後に自動で mocka_write_event を強制する。
// TODO_144 change-tracker / TODO_155 utf8-checker と連携する。

import { ChangeTracker } from './change-tracker.js';
import { RecordStore }   from './change-record-store.js';
import { MocKABridge }   from '../adapters/mocka-bridge.js';
import { UTF8Checker }   from '../validators/utf8-checker.js';

const MOCKA_ENDPOINT     = 'https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev/mcp';
const CONNECT_TIMEOUT_MS = 3000;
const FG_STORE_KEY       = 'file_guard:log';
const MAX_FG_RECORDS     = 200;

// ─── ローカルストア（file-guard 専用）────────────────────────────────────────

const _fgStore = {
  async _get() {
    if (typeof globalThis.chrome !== 'undefined' && chrome.storage?.local) {
      const res = await chrome.storage.local.get(FG_STORE_KEY);
      return res[FG_STORE_KEY] || [];
    }
    return _fgStore._mem;
  },
  _mem: [],
  async _set(records) {
    if (typeof globalThis.chrome !== 'undefined' && chrome.storage?.local) {
      await chrome.storage.local.set({ [FG_STORE_KEY]: records });
    } else {
      _fgStore._mem = records;
    }
  },
  async append(record) {
    const log = await this._get();
    log.push(record);
    const trimmed = log.length > MAX_FG_RECORDS ? log.slice(log.length - MAX_FG_RECORDS) : log;
    await this._set(trimmed);
  },
  async getAll() {
    return this._get();
  },
  async getPending() {
    return (await this._get()).filter(r => !r.mocka_synced);
  },
  async markSynced(id) {
    const log = await this._get();
    await this._set(log.map(r => r.id === id ? { ...r, mocka_synced: true } : r));
  },
};

// ─── ヘルパー ─────────────────────────────────────────────────────────────────

function _makeId() {
  return `FG_${Date.now()}_${Math.random().toString(36).slice(2, 6).toUpperCase()}`;
}

function _parseFile(filePath) {
  const fp   = String(filePath);
  const name = fp.split(/[\\/]/).pop();
  const extM = name.match(/(\.[a-zA-Z0-9]+)$/);
  return { file_name: name, extension: extM ? extM[1] : '' };
}

async function _sendToMocka(title, description, tags, why_purpose) {
  const res = await fetch(MOCKA_ENDPOINT, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      method: 'tools/call',
      params: {
        name: 'mocka_write_event',
        arguments: { title, description, tags, why_purpose },
      },
    }),
    signal: AbortSignal.timeout(CONNECT_TIMEOUT_MS),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

async function _syncRecord(record) {
  const { file_name, extension } = _parseFile(record.file_path);
  const utf8label = record.utf8_verified ? 'PASS' : 'WARNING';
  const tags = `file_guard,${record.type}${extension ? ',' + extension.slice(1) : ''}`;

  await _sendToMocka(
    `${record.type}: ${file_name}`,
    [
      `ファイル操作を記録。`,
      `パス: ${record.file_path}`,
      `UTF-8検証: ${utf8label}`,
      record.context?.reason   ? `理由: ${record.context.reason}` : null,
      record.context?.todo_ref ? `TODO参照: ${record.context.todo_ref}` : null,
      `timestamp: ${record.timestamp}`,
    ].filter(Boolean).join('\n'),
    tags,
    record.context?.reason || 'file-guard',
  );
}

// ─── 公開インターフェース ──────────────────────────────────────────────────────

export const FileGuard = {
  /**
   * create_file 完了直後に呼ぶ。
   * @param {string} filePath
   * @param {object} [context] — { todo_ref?, reason?, session_id? }
   */
  async onFileCreated(filePath, context = {}) {
    // 1. UTF-8 検証（TODO_155）
    const utf8result = await UTF8Checker.verify(filePath);

    // 2. change-tracker に CHANGE_DONE として記録（TODO_144 資産活用）
    await ChangeTracker.afterChange(filePath, utf8result.ok ? 'success' : 'utf8_warning', {
      diff_summary: `FILE_CREATED${utf8result.ok ? '' : ' [UTF-8 WARNING]'}`,
    });

    // 3. file-guard 専用レコードを生成
    const connected = await MocKABridge.isConnected();
    const { file_name, extension } = _parseFile(filePath);
    const record = {
      id:               _makeId(),
      type:             'FILE_CREATED',
      file_path:        filePath,
      file_name,
      extension,
      context:          {
        todo_ref:   context.todo_ref   || '',
        reason:     context.reason     || '',
        session_id: context.session_id || '',
      },
      utf8_verified:    utf8result.ok,
      utf8_issues:      utf8result.issues,
      mocka_synced:     false,
      timestamp:        new Date().toISOString(),
      phi_os_connected: connected,
    };

    await _fgStore.append(record);

    // 4. MoCKA へ即時送信。失敗時はローカル蓄積のまま
    if (connected) {
      try {
        await _syncRecord(record);
        await _fgStore.markSynced(record.id);
        record.mocka_synced = true;
      } catch (err) {
        console.warn('[FileGuard] MoCKA送信失敗（ローカル蓄積）:', err.message);
      }
    }

    console.log('[FileGuard] FILE_CREATED', filePath, `utf8=${utf8result.ok}`, `synced=${record.mocka_synced}`);
    return record;
  },

  /**
   * present_files 完了直後に呼ぶ。
   * @param {string[]} filePaths
   * @param {object} [context]
   */
  async onFilePresented(filePaths, context = {}) {
    const results = [];
    for (const fp of filePaths) {
      const connected = await MocKABridge.isConnected();
      const { file_name, extension } = _parseFile(fp);
      const record = {
        id:               _makeId(),
        type:             'FILE_PRESENTED',
        file_path:        fp,
        file_name,
        extension,
        context:          {
          todo_ref:   context.todo_ref   || '',
          reason:     context.reason     || '',
          session_id: context.session_id || '',
        },
        utf8_verified:    null,
        utf8_issues:      [],
        mocka_synced:     false,
        timestamp:        new Date().toISOString(),
        phi_os_connected: connected,
      };

      await _fgStore.append(record);

      if (connected) {
        try {
          await _syncRecord(record);
          await _fgStore.markSynced(record.id);
          record.mocka_synced = true;
        } catch (err) {
          console.warn('[FileGuard] MoCKA送信失敗（ローカル蓄積）:', err.message);
        }
      }

      results.push(record);
    }

    console.log('[FileGuard] FILE_PRESENTED', filePaths.length, 'files');
    return results;
  },

  /**
   * 未記録（mocka_synced: false）のファイル一覧を返す。
   */
  async getUnsyncedFiles() {
    return _fgStore.getPending();
  },

  /**
   * 全未送信レコードを MoCKA へ強制送信する。
   * @returns {Promise<{ sent: number, failed: number }>}
   */
  async forceSync() {
    const pending = await _fgStore.getPending();
    let sent = 0, failed = 0;

    for (const record of pending) {
      try {
        await _syncRecord(record);
        await _fgStore.markSynced(record.id);
        sent++;
      } catch {
        failed++;
      }
    }

    console.log(`[FileGuard] forceSync: sent=${sent} failed=${failed}`);
    return { sent, failed };
  },
};
