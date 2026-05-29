// phi-adapter.js — 各製品に同梱する共通アダプター
// Orchestra / Relay / Memory がこのファイルをコピーして使用する
'use strict';

const PHI_OS_STORAGE_PREFIX = 'phi_';

/**
 * PHI OS IndexedDB Hubが利用可能かを判定する
 * PHI OS未インストール時も graceful degradation で動作する
 */
async function isPHIOsAvailable() {
  try {
    const db = await new Promise((resolve, reject) => {
      const req = indexedDB.open('phi-os-hub', 1);
      req.onsuccess = (e) => resolve(e.target.result);
      req.onerror   = ()  => resolve(null);
    });
    return !!db;
  } catch {
    return false;
  }
}

export const PHI_ADAPTER = {
  /**
   * 名前空間付きでデータを書き込む
   * PHI OS存在時はIndexedDB Hubにも同期、なければchrome.storage.localのみ
   * @param {string} namespace  製品名 (e.g. 'relay', 'orchestra')
   * @param {string} key
   * @param {*} value
   */
  async write(namespace, key, value) {
    const storageKey = `${PHI_OS_STORAGE_PREFIX}${namespace}_${key}`;
    try {
      await chrome.storage.local.set({ [storageKey]: value });
    } catch (e) {
      console.error('[PHI Adapter] write error:', e);
      throw e;
    }
  },

  /**
   * 名前空間付きでデータを読み込む
   * @param {string} namespace
   * @param {string} key
   * @param {*} defaultValue
   * @returns {Promise<*>}
   */
  async read(namespace, key, defaultValue = undefined) {
    const storageKey = `${PHI_OS_STORAGE_PREFIX}${namespace}_${key}`;
    try {
      const stored = await chrome.storage.local.get(storageKey);
      return storageKey in stored ? stored[storageKey] : defaultValue;
    } catch (e) {
      console.error('[PHI Adapter] read error:', e);
      return defaultValue;
    }
  },

  /**
   * PHI OSに対してイベントを通知する（commit完了通知など）
   * @param {string} eventType
   * @param {object} payload
   */
  async notify(eventType, payload) {
    try {
      await chrome.storage.local.set({
        phi_event_latest: { type: eventType, payload, ts: Date.now() },
      });
    } catch (e) {
      console.error('[PHI Adapter] notify error:', e);
    }
  },

  /**
   * PHI OSからの最新イベントを取得してクリアする
   * @returns {Promise<object|null>}
   */
  async pollEvent() {
    try {
      const stored = await chrome.storage.local.get('phi_event_latest');
      const event  = stored['phi_event_latest'] || null;
      if (event) await chrome.storage.local.remove('phi_event_latest');
      return event;
    } catch {
      return null;
    }
  },
};
