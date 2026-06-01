// state-store.js — L1(memory)/L2(storage.local)/L3(IndexedDB) 3層キャッシュ
'use strict';

import { reportError } from '../debug/error-reporter.js';

// L1: インメモリキャッシュ（ページ生存中のみ有効）
const L1 = new Map();

// MoCKA接続確認結果キャッシュ（30秒TTL）
let _modeCache     = null;
let _modeCacheTime = 0;
const MODE_CACHE_TTL_MS = 30000;

/**
 * 動作モードを返す。結果は30秒キャッシュ。
 * @returns {Promise<'STANDALONE'|'CONNECTED'>}
 */
export async function detectMode() {
  if (_modeCache && Date.now() - _modeCacheTime < MODE_CACHE_TTL_MS) {
    return _modeCache;
  }
  try {
    // 設定でConnectedを明示的にOFFにしている場合はSTANDALONE固定
    const { phi_connected_mode } = await chrome.storage.local.get('phi_connected_mode');
    if (phi_connected_mode === false) {
      _modeCache = 'STANDALONE';
      _modeCacheTime = Date.now();
      return _modeCache;
    }
    const res = await fetch('http://localhost:5000/b/health', {
      signal: AbortSignal.timeout(500),
    });
    _modeCache = res.ok ? 'CONNECTED' : 'STANDALONE';
  } catch {
    _modeCache = 'STANDALONE';
  }
  _modeCacheTime = Date.now();
  return _modeCache;
}

/**
 * キャッシュを無効化して次回detectModeで再確認させる
 */
export function invalidateModeCache() {
  _modeCache = null;
  _modeCacheTime = 0;
}

// ─── L2: chrome.storage.local ────────────────────────────────────────────────

/**
 * L1→L2の順で書き込む
 * @param {string} key
 * @param {*} value
 */
export async function set(key, value) {
  L1.set(key, value);
  try {
    await chrome.storage.local.set({ [key]: value });
  } catch (e) {
    await reportError({ type: 'STORAGE_WRITE_ERROR', message: e.message, key, ts: Date.now() });
    throw e;
  }
}

/**
 * L1優先で読み込む。L1にない場合はL2から取得してL1に積む。
 * @param {string} key
 * @param {*} defaultValue
 * @returns {Promise<*>}
 */
export async function get(key, defaultValue = undefined) {
  if (L1.has(key)) return L1.get(key);
  try {
    const stored = await chrome.storage.local.get(key);
    const value = key in stored ? stored[key] : defaultValue;
    if (value !== undefined) L1.set(key, value);
    return value;
  } catch (e) {
    await reportError({ type: 'STORAGE_READ_ERROR', message: e.message, key, ts: Date.now() });
    return defaultValue;
  }
}

/**
 * L1・L2両方から削除
 * @param {string} key
 */
export async function remove(key) {
  L1.delete(key);
  try {
    await chrome.storage.local.remove(key);
  } catch (e) {
    await reportError({ type: 'STORAGE_REMOVE_ERROR', message: e.message, key, ts: Date.now() });
  }
}

/**
 * ストレージ使用量をバイト単位で返す
 * @returns {Promise<number>}
 */
export async function getBytesInUse() {
  try {
    return await chrome.storage.local.getBytesInUse();
  } catch {
    return 0;
  }
}

/**
 * L3: phi_ プレフィックスキーの全データを JSON として一括出力する（Snapshot Export）
 * options.html のダッシュボードやデバッグツールから利用する
 * @returns {Promise<object>}  { ts, bytesInUse, keys: { [key]: value } }
 */
export async function snapshot() {
  try {
    const all   = await chrome.storage.local.get(null);
    const phiKeys = Object.fromEntries(
      Object.entries(all).filter(([k]) => k.startsWith('phi_'))
    );
    return {
      ts:          Date.now(),
      bytesInUse:  await getBytesInUse(),
      keyCount:    Object.keys(phiKeys).length,
      keys:        phiKeys,
    };
  } catch (e) {
    await reportError({ type: 'SNAPSHOT_ERROR', message: e.message, ts: Date.now() });
    return { ts: Date.now(), bytesInUse: 0, keyCount: 0, keys: {} };
  }
}

// ─── L3: IndexedDB (content.js専用 — background.jsからは呼ばない) ─────────────

const IDB_NAME    = 'phi-os-hub';
const IDB_VERSION = 1;
const IDB_STORE   = 'commits';

function openIDB() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(IDB_NAME, IDB_VERSION);
    req.onupgradeneeded = (e) => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains(IDB_STORE)) {
        db.createObjectStore(IDB_STORE, { keyPath: 'commit_id' });
      }
    };
    req.onsuccess = (e) => resolve(e.target.result);
    req.onerror   = (e) => reject(e.target.error);
  });
}

/**
 * IndexedDBにコミットを保存する（content.jsからのみ呼び出す）
 * @param {object} packet
 */
export async function idbSaveCommit(packet) {
  try {
    const db = await openIDB();
    return new Promise((resolve, reject) => {
      const tx    = db.transaction(IDB_STORE, 'readwrite');
      const store = tx.objectStore(IDB_STORE);
      store.put(packet);
      tx.oncomplete = () => resolve();
      tx.onerror    = (e) => reject(e.target.error);
    });
  } catch (e) {
    await reportError({ type: 'IDB_WRITE_ERROR', message: e.message, ts: Date.now() });
    throw e;
  }
}

/**
 * IndexedDBから最新N件のコミットを返す（content.jsからのみ呼び出す）
 * @param {number} limit
 * @returns {Promise<Array>}
 */
export async function idbGetRecentCommits(limit = 5) {
  try {
    const db = await openIDB();
    return new Promise((resolve, reject) => {
      const tx      = db.transaction(IDB_STORE, 'readonly');
      const store   = tx.objectStore(IDB_STORE);
      const results = [];
      const cursor  = store.openCursor(null, 'prev');
      cursor.onsuccess = (e) => {
        const c = e.target.result;
        if (c && results.length < limit) {
          results.push(c.value);
          c.continue();
        } else {
          resolve(results);
        }
      };
      cursor.onerror = (e) => reject(e.target.error);
    });
  } catch (e) {
    await reportError({ type: 'IDB_READ_ERROR', message: e.message, ts: Date.now() });
    return [];
  }
}
