/**
 * mini MoCKA Core SDK — bridge/inter-product.js
 * Inter-product event bus via chrome.runtime messaging.
 * Allows e.g. Relay to hand off session data to Vault.
 */

const _handlers = {};

export const MockaBridge = {
  /**
   * Emit an event to other products / background scripts.
   * @param {string} event - e.g. 'relay:handoff', 'vault:save'
   * @param {any} data
   */
  emit(event, data) {
    chrome.runtime.sendMessage({ type: 'MOCKA_BRIDGE', event, data }, () => {
      if (chrome.runtime.lastError) {
        // Suppress "no receiver" error — other products may not be active
      }
    });
    // Also dispatch locally for same-context listeners
    window.dispatchEvent(new CustomEvent(`mocka:${event}`, { detail: data }));
  },

  /**
   * Listen for bridge events.
   */
  on(event, handler) {
    if (!_handlers[event]) _handlers[event] = [];
    _handlers[event].push(handler);
    window.addEventListener(`mocka:${event}`, (e) => handler(e.detail));
  },

  off(event, handler) {
    if (!_handlers[event]) return;
    _handlers[event] = _handlers[event].filter(h => h !== handler);
  },

  /**
   * Register background script listener (call from background.js).
   */
  initBackground() {
    chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
      if (msg.type !== 'MOCKA_BRIDGE') return;
      const { event, data } = msg;
      (_handlers[event] || []).forEach(h => h(data));
      sendResponse({ ok: true });
    });
  }
};
