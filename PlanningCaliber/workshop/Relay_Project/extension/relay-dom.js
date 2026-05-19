/**
 * Relay — relay-dom.js
 * @version 3.2.0
 * @description claude.ai DOM操作の集中管理。セレクタ・テキスト取得・入力注入。
 *
 * Purpose  : DOM へのアクセスを1ファイルに集約。セレクタ drift への対応を一元化。
 * Owns     : querySelector with fallback / getText / injectText
 * Must not : state への書き込み・chrome API・localStorage
 * Inputs   : DOM (document)
 * Outputs  : 取得テキスト・注入結果
 *
 * Known traps:
 *   - claude.ai のDOM更新でセレクタが無効になる。SELECTORS配列の先頭から試す。
 *   - assistantMessage は複数あることが多い。lastElementChild で最新を取る。
 *   - contenteditable な input は value ではなく textContent で読む。
 */

(() => {
  'use strict';

  const Relay = globalThis.__RELAY__;
  if (!Relay) { console.error('[Relay] relay-dom.js: __RELAY__ not found'); return; }

  // ─── セレクタレジストリ ──────────────────────────────────────────────────────
  // confidence順で試行。claude.ai更新時はここだけ直す。

  const SELECTORS = {
    assistantMessage: [
      '[data-testid="assistant-message"]',
      '.font-claude-message',
      '.font-claude-response',
      '[class*="assistant"]',
    ],
    userMessage: [
      '[data-testid="user-message"]',
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

  // ─── 汎用クエリ（フォールバック付き）────────────────────────────────────────

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

  // ─── テキスト取得 ────────────────────────────────────────────────────────────

  /**
   * 最新のアシスタントメッセージテキストを返す。
   * @returns {string}
   */
  function getLatestAssistantText() {
    const els = queryAll(SELECTORS.assistantMessage);
    if (els.length === 0) return '';
    const last = els[els.length - 1];
    return (last.innerText ?? last.textContent ?? '').trim();
  }

  /**
   * 最新のユーザーメッセージテキストを返す。
   * @returns {string}
   */
  function getLatestUserText() {
    const els = queryAll(SELECTORS.userMessage);
    if (els.length === 0) return '';
    const last = els[els.length - 1];
    return (last.innerText ?? last.textContent ?? '').trim();
  }

  /**
   * 全アシスタントメッセージをテキスト配列で返す。
   */
  function getAllAssistantTexts() {
    return queryAll(SELECTORS.assistantMessage)
      .map(el => (el.innerText ?? el.textContent ?? '').trim())
      .filter(t => t.length > 0);
  }

  /**
   * 全会話テキストを role 付き配列で返す。
   * @returns {{role: 'user'|'assistant', text: string}[]}
   */
  function getAllMessages() {
    const messages = [];
    // すべての会話コンテナを順に取得
    const allUser      = queryAll(SELECTORS.userMessage);
    const allAssistant = queryAll(SELECTORS.assistantMessage);

    // DOM順に並べて role を付与
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

  /**
   * 現在のページURLを返す。
   */
  function getCurrentUrl() {
    return window.location.href;
  }

  /**
   * 現在のchatページかどうかを返す。
   */
  function isChatPage() {
    return /claude\.ai\/(chat|new)/.test(getCurrentUrl());
  }

  /**
   * ターン数を DOM から取得する。
   */
  function getTurnCount() {
    return queryAll(SELECTORS.assistantMessage).length;
  }

  // ─── テキスト注入 ────────────────────────────────────────────────────────────

  /**
   * input ボックスにテキストを注入する。
   * @param {string} text
   * @returns {boolean} 成功したか
   */
  function injectText(text) {
    const el = queryFirst(SELECTORS.inputBox);
    if (!el) return false;

    try {
      el.focus();

      if (el.tagName === 'TEXTAREA') {
        el.value = text;
        el.dispatchEvent(new Event('input', { bubbles: true }));
      } else {
        // contenteditable
        el.textContent = text;
        // React の onChange を発火させるために execCommand を使う
        document.execCommand('insertText', false, '');
        el.dispatchEvent(new InputEvent('input', { bubbles: true, data: text }));
      }
      return true;
    } catch (e) {
      console.warn('[Relay] injectText failed:', e);
      return false;
    }
  }

  /**
   * テキストをクリップボードにコピーする。
   * @param {string} text
   */
  async function copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (_) {
      // フォールバック: execCommand
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

  // ─── サービスとして登録 ───────────────────────────────────────────────────────

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

  console.info('[Relay] relay-dom.js registered.');

})();
