/**
 * mini MoCKA Core SDK — summary/injector.js
 * Injects context text into a claude.ai chat input.
 * Used by: Relay (handoff), Vault (context restore)
 */

const INPUT_SELECTORS = [
  'div[contenteditable="true"][data-placeholder]',
  'div[contenteditable="true"].ProseMirror',
  'textarea[data-id="root"]',
];

function findInput() {
  for (const sel of INPUT_SELECTORS) {
    const el = document.querySelector(sel);
    if (el) return el;
  }
  return null;
}

function simulateInput(el, text) {
  el.focus();
  if (el.tagName === 'TEXTAREA') {
    const nativeSet = Object.getOwnPropertyDescriptor(
      window.HTMLTextAreaElement.prototype, 'value'
    ).set;
    nativeSet.call(el, text);
  } else {
    el.textContent = text;
    const range = document.createRange();
    const sel = window.getSelection();
    range.setStart(el, el.childNodes.length);
    range.collapse(true);
    sel.removeAllRanges();
    sel.addRange(range);
  }
  el.dispatchEvent(new Event('input', { bubbles: true }));
  el.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertText', data: text }));
}

export const MockaInjector = {
  /**
   * Inject text into the claude.ai chat input.
   * @param {string} text
   * @param {{ autoSubmit?: boolean, delay?: number }} options
   * @returns {Promise<boolean>}
   */
  async inject(text, options = {}) {
    const { autoSubmit = false, delay = 300 } = options;

    await new Promise(r => setTimeout(r, delay));

    const input = findInput();
    if (!input) {
      console.warn('[MoCKA Injector] Input not found');
      return false;
    }

    simulateInput(input, text);

    if (autoSubmit) {
      await new Promise(r => setTimeout(r, 200));
      input.dispatchEvent(new KeyboardEvent('keydown', {
        key: 'Enter', code: 'Enter', bubbles: true
      }));
    }

    return true;
  },

  /**
   * Open a new claude.ai chat and inject after navigation.
   * @param {string} text
   */
  async openNewChatAndInject(text) {
    const newTabUrl = 'https://claude.ai/new';
    chrome.tabs.create({ url: newTabUrl }, (tab) => {
      const listener = (tabId, info) => {
        if (tabId !== tab.id || info.status !== 'complete') return;
        chrome.tabs.onUpdated.removeListener(listener);
        setTimeout(() => {
          chrome.tabs.sendMessage(tab.id, {
            type: 'MOCKA_INJECT',
            payload: { text }
          });
        }, 1500);
      };
      chrome.tabs.onUpdated.addListener(listener);
    });
  }
};
