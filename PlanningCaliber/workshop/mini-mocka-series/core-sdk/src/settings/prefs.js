/**
 * mini MoCKA Core SDK — settings/prefs.js
 * Shared user preferences across all products.
 */

const PREFS_KEY = 'mocka_global_prefs';

const DEFAULTS = {
  turnLimit: 20,
  language: 'en',
  autoSave: true,
  showBadge: true,
  summaryStyle: 'relay',
  exportFormat: 'json',
  vaultAutoPropose: true,
  logbookAutoExtract: false,
  prismModeDefault: 'deep-dive',
};

export const MockaPrefs = {
  async getAll() {
    return new Promise(resolve => {
      chrome.storage.sync.get(PREFS_KEY, result => {
        resolve({ ...DEFAULTS, ...(result[PREFS_KEY] || {}) });
      });
    });
  },

  async get(key, defaultValue) {
    const all = await this.getAll();
    return all[key] ?? defaultValue ?? DEFAULTS[key] ?? null;
  },

  async set(key, value) {
    const all = await this.getAll();
    const updated = { ...all, [key]: value };
    return new Promise(resolve => {
      chrome.storage.sync.set({ [PREFS_KEY]: updated }, () => resolve(true));
    });
  },

  async reset() {
    return new Promise(resolve => {
      chrome.storage.sync.remove(PREFS_KEY, () => resolve(true));
    });
  }
};
