/**
 * mini MoCKA Core SDK — dom/watcher.js
 * Fresh implementation. Reference to Orchestra content.js only for selectors.
 * No MoCKA hooks, no DNA injection, no essence pipeline.
 */

const SELECTORS = {
  turnContainer: '[data-testid="conversation-turn"]',
  userBubble: '[data-testid="user-human-turn"]',
  aiBubble: '[data-testid="ai-turn"]',
  textarea: 'div[contenteditable="true"][data-placeholder]',
};

let _observer = null;
let _turnCount = 0;
let _callbacks = { onTurn: null, onMessage: null, onNewChat: null };
let _lastUrl = location.href;

function _countTurns() {
  return document.querySelectorAll(SELECTORS.turnContainer).length;
}

function _detectUrlChange() {
  const current = location.href;
  if (current !== _lastUrl) {
    _lastUrl = current;
    _turnCount = 0;
    _callbacks.onNewChat?.({ url: current });
  }
}

function _observe() {
  if (_observer) _observer.disconnect();

  _observer = new MutationObserver(() => {
    _detectUrlChange();
    const count = _countTurns();
    if (count !== _turnCount) {
      _turnCount = count;
      _callbacks.onTurn?.({ count: _turnCount });

      const turns = document.querySelectorAll(SELECTORS.turnContainer);
      const last = turns[turns.length - 1];
      if (last) {
        const role = last.querySelector(SELECTORS.userBubble) ? 'user' : 'assistant';
        const text = last.innerText?.trim() || '';
        _callbacks.onMessage?.({ role, text, turn: _turnCount, ts: Date.now() });
      }
    }
  });

  _observer.observe(document.body, { childList: true, subtree: true });
}

export const MockaWatcher = {
  /**
   * Start watching.
   * @param {{ onTurn?, onMessage?, onNewChat? }} options
   */
  init(options = {}) {
    _callbacks = { ...options };
    _turnCount = _countTurns();
    _observe();

    window.addEventListener('popstate', _detectUrlChange);
    const _pushState = history.pushState.bind(history);
    history.pushState = function(...args) {
      _pushState(...args);
      _detectUrlChange();
    };
  },

  getTurnCount() { return _turnCount; },

  /**
   * Snapshot of all current messages in DOM.
   */
  getMessages() {
    const turns = [...document.querySelectorAll(SELECTORS.turnContainer)];
    return turns.map((el, i) => {
      const isUser = !!el.querySelector(SELECTORS.userBubble);
      return {
        role: isUser ? 'user' : 'assistant',
        text: el.innerText?.trim() || '',
        turn: i + 1,
        ts: null
      };
    });
  },

  destroy() {
    _observer?.disconnect();
    _observer = null;
    _callbacks = {};
    window.removeEventListener('popstate', _detectUrlChange);
  }
};
