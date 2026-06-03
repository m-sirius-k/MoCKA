'use strict';
// change-record-store.js — ローカルログ管理
// chrome.storage.local に変更レコードを蓄積する。PHI-OS未接続でも単独動作。

const STORE_KEY  = 'change_tracker:log';
const STATS_KEY  = 'change_tracker:stats';
const MAX_RECORDS = 200;

// chrome.storage.local が使えない環境（Node.js等）向けのメモリ fallback
const _memStore = { log: [], stats: { total_lifetime: 0, last_flush: null } };

function _hasStorage() {
  return typeof globalThis.chrome !== 'undefined' && chrome.storage?.local;
}

async function _getLog() {
  if (!_hasStorage()) return [..._memStore.log];
  const res = await chrome.storage.local.get(STORE_KEY);
  return res[STORE_KEY] || [];
}

async function _setLog(records) {
  if (!_hasStorage()) { _memStore.log = records; return; }
  await chrome.storage.local.set({ [STORE_KEY]: records });
}

async function _getStats() {
  if (!_hasStorage()) return { ..._memStore.stats };
  const res = await chrome.storage.local.get(STATS_KEY);
  return res[STATS_KEY] || { total_lifetime: 0, last_flush: null };
}

async function _setStats(stats) {
  if (!_hasStorage()) { _memStore.stats = stats; return; }
  await chrome.storage.local.set({ [STATS_KEY]: stats });
}

export const RecordStore = {
  async append(record) {
    const log = await _getLog();
    log.push(record);
    // 200件超過時は古い順に削除
    const trimmed = log.length > MAX_RECORDS ? log.slice(log.length - MAX_RECORDS) : log;
    await _setLog(trimmed);

    const stats = await _getStats();
    stats.total_lifetime = (stats.total_lifetime || 0) + 1;
    await _setStats(stats);
  },

  async getAll() {
    return _getLog();
  },

  async getPending() {
    const log = await _getLog();
    return log.filter(r => !r.mocka_synced);
  },

  async markSynced(id) {
    const log = await _getLog();
    const updated = log.map(r => r.id === id ? { ...r, mocka_synced: true } : r);
    await _setLog(updated);
  },

  async clear() {
    await _setLog([]);
  },

  async getStats() {
    const log   = await _getLog();
    const stats = await _getStats();
    return {
      total:         log.length,
      pending:       log.filter(r => !r.mocka_synced).length,
      synced:        log.filter(r =>  r.mocka_synced).length,
      total_lifetime: stats.total_lifetime || 0,
      last_flush:    stats.last_flush || null,
    };
  },

  async updateLastFlush() {
    const stats = await _getStats();
    stats.last_flush = new Date().toISOString();
    await _setStats(stats);
  },
};
