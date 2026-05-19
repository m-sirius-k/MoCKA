/**
 * Relay - relay-dom.js
 * @version 3.3.0
 * @description claude.ai DOM操作の集中管理。セレクタ・テキスト取得・入力注入。
 *
 * Purpose  : DOM へのアクセスをこのファイルに集中。セレクタ drift への対応を一元化。
 * Owns     : querySelector with fallback / getText / injectText
 * Must not : state への書き込み・chrome API・localStorage
 * Inputs   : DOM (document)
 * Outputs  : 取得テキスト・注入結果
 *
 * Known traps:
 *   - claude.ai のDOM更新でセレクタが無効になる。SELECTORSの先頭から試す。
 *   - assistantMessage は複数あることが多い。lastElementChild で最新を取る。
 *   - contenteditable な input は value ではなく textContent で読む。
 *
 * v3.3.0 変更: assistantMessage セレクタを .font-claude-response に更新
 *              (旧 .font-claude-message / [data-testid="assistant-message"] は消滅)
 */

(() => {
  'use strict';

  const Relay = globalThis.__RELAY__;
  if (!Relay) { console.error('[Relay] relay-dom.js: __RELAY__ not found'); return; }

  // ─── セレクタレジストリ ────────────────────────────────────────────────────
  // confidence順で試行。claude.ai更新時はここだけ変える。
  const SELECTORS = {
    assistantMessage: [
      '.font-claude-response',          // 2026-05 現行
      '[data-testid="assistant-message"]',
      '.font-claude-message',
      '[class*="claude-response"]',
      '[class*="assistant"]',
    ],
    userMessage: [
      '[data-testid="user-message"]',   // 2026-05 現行
      '.font-user-message',
      '[class*="human"]',
    ],
    inputBox: [
      'div[contenteditable="true"][data-placeholder]',
      'div[contenteditable="true"].ProseMirror',
      'div[contenteditable="true"]',
      'textarea',
    ],
    sendButton: [
      'button[aria-label="Send message"]',
      'button[data-testid="send-button"]',
      'button[type="submit"]',
    ],
    newChatLink: [
      'a[href="/new"]',
      'a[href*="new"]',
    ],
  };

  // ─── 汎用クエリ（フォールバック付き）────────────────────────────────────

  function queryFirst(candidates, root = document) {
    for (const sel of candidates) {
      try {
        const el = root.querySelector(sel);
        if (el) return el;
      } catch (_) { /* 無効セレクタはスキップ */ }
    }
    return null;
  }

  function queryAll(candidates, root = document) {
    for (const sel of candidates) {
      try {
        const els = root.querySelectorAll(sel);
        if (els.length > 0) return Array.from(els);
      } catch (_) { /* skip */ }
    }
    return [];
  }

  // ─── テキスト取得 ────────────────────────────────────────────────────────

  function getLatestAssistantText() {
    const els = queryAll(SELECTORS.assistantMessage);
    if (els.length === 0) return '';
    const last = els[els.length - 1];
    return (last.innerText ?? last.textContent ?? '').trim();
  }

  function getLatestUserText() {
    const els = queryAll(SELECTORS.userMessage);
    if (els.length === 0) return '';
    const last = els[els.length - 1];
    return (last.innerText ?? last.textContent ?? '').trim();
  }

  function getAllAssistantTexts() {
    return queryAll(SELECTORS.assistantMessage)
      .map(el => (el.innerText ?? el.textContent ?? '').trim())
      .filter(t => t.length > 0);
  }

  function getAllMessages() {
    const messages = [];
    const allUser      = queryAll(SELECTORS.userMessage);
    const allAssistant = queryAll(SELECTORS.assistantMessage);

    const allEls = [
      ...allUser.map(el => ({ el, role: 'user' })),
      ...allAssistant.map(el => ({ el, role: 'assistant' })),
    ].sort((a, b) =>
      a.el.compareDocumentPosition(b.el) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1
    );

    for (const { el, role } of allEls) {
      const text = (el.innerText ?? el.textContent ?? '').trim();
      if (text.length > 0) messages.push({ role, text });
    }
    return messages;
  }

  function getCurrentUrl() {
    return window.location.href;
  }

  function isChatPage() {
    return /claude\.ai\/(chat|new)/.test(getCurrentUrl());
  }

  /**
   * ターン数 = アシスタントメッセージ数
   */
  function getTurnCount() {
    return queryAll(SELECTORS.assistantMessage).length;
  }

  // ─── テキスト注入 ────────────────────────────────────────────────────────

  function injectText(text) {
    const el = queryFirst(SELECTORS.inputBox);
    if (!el) return false;

    try {
      el.focus();

      if (el.tagName === 'TEXTAREA') {
        el.value = text;
        el.dispatchEvent(new Event('input', { bubbles: true }));
      } else {
        el.textContent = text;
        document.execCommand('insertText', false, '');
        el.dispatchEvent(new InputEvent('input', { bubbles: true, data: text }));
      }
      return true;
    } catch (e) {
      console.warn('[Relay] injectText failed:', e);
      return false;
    }
  }

  async function copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (_) {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity  = '0';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      return true;
    }
  }

  // ─── サービスとして登録 ──────────────────────────────────────────────────

  Relay.services.dom = Object.freeze({
    queryFirst,
    queryAll,
    getLatestAssistantText,
    getLatestUserText,
    getAllAssistantTexts,
    getAllMessages,
    getCurrentUrl,
    isChatPage,
    getTurnCount,
    injectText,
    copyToClipboard,
    SELECTORS,
  });

  console.info('[Relay] relay-dom.js registered. v3.3.0');

})();
