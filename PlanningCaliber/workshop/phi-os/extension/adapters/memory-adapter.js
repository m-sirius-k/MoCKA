// memory-adapter.js — Memory 専用アダプター（将来実装用骨格）
'use strict';

import { PHI_ADAPTER } from './phi-adapter.js';
import { emit }        from '../core/event-bus.js';

export const MEMORY_ADAPTER = {
  /**
   * Memory の制約・決定データを PHI OS Hub に書き込む
   * @param {object} memoryData  { type: 'env'|'error'|'decision', content: string }
   */
  async syncMemory(memoryData) {
    await PHI_ADAPTER.write('memory', `entry_${Date.now()}`, memoryData);
    await emit('MEMORY_SYNC', { type: memoryData.type, ts: Date.now() });
  },

  /**
   * 最新のMemoryエントリを取得する
   * @param {number} limit
   * @returns {Promise<Array>}
   */
  async getRecentEntries(limit = 10) {
    // chrome.storage.local から phi_memory_ プレフィックスのキーを検索
    try {
      const all    = await chrome.storage.local.get(null);
      const entries = Object.entries(all)
        .filter(([k]) => k.startsWith('phi_memory_entry_'))
        .map(([, v]) => v)
        .sort((a, b) => (b.ts || 0) - (a.ts || 0))
        .slice(0, limit);
      return entries;
    } catch {
      return [];
    }
  },
};
