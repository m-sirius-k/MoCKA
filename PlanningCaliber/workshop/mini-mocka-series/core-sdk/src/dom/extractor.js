/**
 * mini MoCKA Core SDK — dom/extractor.js
 * Extracts structured conversation data from claude.ai DOM.
 */

import { MockaWatcher } from './watcher.js';

export const MockaExtractor = {
  /**
   * Full conversation snapshot.
   * @returns {{ turns, url, sessionId, title }}
   */
  getConversation() {
    const turns = MockaWatcher.getMessages();
    const url = location.href;
    const sessionId = url.match(/\/chat\/([a-zA-Z0-9-]+)/)?.[1] || null;
    const title = document.title?.replace(' - Claude', '').trim() || 'Untitled';
    return { turns, url, sessionId, title };
  },

  /**
   * Last N turns.
   */
  getLastN(n) {
    const turns = MockaWatcher.getMessages();
    return turns.slice(-n);
  },

  /**
   * User messages only.
   */
  getUserMessages() {
    return MockaWatcher.getMessages().filter(m => m.role === 'user');
  },

  /**
   * Check if currently on a claude.ai chat page.
   */
  isOnChatPage() {
    return /claude\.ai\/(chat|new)/.test(location.href);
  }
};
