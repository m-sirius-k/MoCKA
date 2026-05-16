/**
 * mini MoCKA Core SDK — storage/store.js
 * Namespaced chrome.storage.local abstraction
 * No MoCKA dependencies. Works standalone.
 */

export class MockaStore {
  constructor(namespace) {
    if (!namespace) throw new Error('MockaStore: namespace required');
    this._ns = `mocka_${namespace}_`;
  }

  _key(k) { return `${this._ns}${k}`; }

  async set(key, value) {
    return new Promise((resolve, reject) => {
      chrome.storage.local.set({ [this._key(key)]: value }, () => {
        if (chrome.runtime.lastError) reject(chrome.runtime.lastError);
        else resolve(true);
      });
    });
  }

  async get(key) {
    return new Promise((resolve, reject) => {
      chrome.storage.local.get(this._key(key), (result) => {
        if (chrome.runtime.lastError) reject(chrome.runtime.lastError);
        else resolve(result[this._key(key)] ?? null);
      });
    });
  }

  async delete(key) {
    return new Promise((resolve, reject) => {
      chrome.storage.local.remove(this._key(key), () => {
        if (chrome.runtime.lastError) reject(chrome.runtime.lastError);
        else resolve(true);
      });
    });
  }

  async list() {
    return new Promise((resolve, reject) => {
      chrome.storage.local.get(null, (all) => {
        if (chrome.runtime.lastError) { reject(chrome.runtime.lastError); return; }
        const entries = Object.entries(all)
          .filter(([k]) => k.startsWith(this._ns))
          .map(([k, v]) => ({ key: k.slice(this._ns.length), value: v }));
        resolve(entries);
      });
    });
  }

  async clear() {
    const entries = await this.list();
    const keys = entries.map(e => this._key(e.key));
    return new Promise((resolve, reject) => {
      chrome.storage.local.remove(keys, () => {
        if (chrome.runtime.lastError) reject(chrome.runtime.lastError);
        else resolve(true);
      });
    });
  }
}
