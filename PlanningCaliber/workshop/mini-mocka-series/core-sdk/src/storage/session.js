/**
 * mini MoCKA Core SDK — storage/session.js
 * Session record management. Migrated from Orchestra storage pattern.
 * Supports all products: orchestra, relay, vault, logbook, prism
 */

import { MockaStore } from './store.js';

const INDEX_KEY = '__index__';
const store = new MockaStore('sessions');

function uuid() {
  return crypto.randomUUID
    ? crypto.randomUUID()
    : 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
        const r = Math.random() * 16 | 0;
        return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
      });
}

async function getIndex() {
  return (await store.get(INDEX_KEY)) || [];
}

async function setIndex(index) {
  return store.set(INDEX_KEY, index);
}

export const MockaSession = {
  /**
   * Save a new session record.
   * @param {Object} data - { product, title, url, messages, tags? }
   * @returns {string} sessionId
   */
  async save(data) {
    const id = uuid();
    const now = new Date().toISOString();
    const session = {
      id,
      product: data.product || 'unknown',
      title: data.title || 'Untitled',
      url: data.url || '',
      turns: data.messages?.length || 0,
      messages: data.messages || [],
      tags: data.tags || [],
      createdAt: now,
      updatedAt: now,
    };
    await store.set(id, session);
    const index = await getIndex();
    index.unshift({ id, product: session.product, title: session.title,
      turns: session.turns, createdAt: now });
    await setIndex(index);
    return id;
  },

  /**
   * Get all sessions (index only, no messages).
   * @param {string} [product] - filter by product name
   */
  async getAll(product) {
    const index = await getIndex();
    if (product) return index.filter(s => s.product === product);
    return index;
  },

  /**
   * Get full session by id (includes messages).
   */
  async getById(id) {
    return store.get(id);
  },

  /**
   * Full-text search across session titles and messages.
   */
  async search(query) {
    const index = await getIndex();
    const q = query.toLowerCase();
    const matched = [];
    for (const entry of index) {
      if (entry.title.toLowerCase().includes(q)) {
        matched.push(entry); continue;
      }
      const full = await store.get(entry.id);
      if (!full) continue;
      const hit = full.messages.some(m => m.text?.toLowerCase().includes(q));
      if (hit) matched.push(entry);
    }
    return matched;
  },

  /**
   * Delete a session by id.
   */
  async delete(id) {
    await store.delete(id);
    const index = await getIndex();
    await setIndex(index.filter(s => s.id !== id));
    return true;
  },

  /**
   * Get total counts.
   */
  async stats() {
    const index = await getIndex();
    const totalMessages = index.reduce((s, e) => s + (e.turns || 0), 0);
    return { sessions: index.length, messages: totalMessages };
  }
};
