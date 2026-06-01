// relay-dom.js — DOM ユーティリティ（claude.ai セレクター定義）
// health_check.py が毎朝このセレクターの生存を確認する（TIC Layer 0）
'use strict';

window.RelayDOM = (() => {
  // claude.ai のターン要素セレクター（DOM変更時はここを更新）
  const SELECTORS = {
    humanTurn:   '[data-testid="human-turn"]',
    aiTurn:      '[data-testid="ai-turn"]',
    inputEditor: 'div[contenteditable="true"]',
    mainContent: 'main',
  };

  return {
    getSelectors: () => ({ ...SELECTORS }),

    /**
     * ページ上の全ターン要素を返す
     */
    getAllTurns() {
      return [
        ...document.querySelectorAll(SELECTORS.humanTurn),
        ...document.querySelectorAll(SELECTORS.aiTurn),
      ].sort((a, b) => {
        const posA = a.getBoundingClientRect().top;
        const posB = b.getBoundingClientRect().top;
        return posA - posB;
      });
    },

    /**
     * ターン要素からロールとテキストを抽出する
     */
    extractTurn(el) {
      const isHuman = el.matches(SELECTORS.humanTurn);
      return {
        role:    isHuman ? 'user' : 'assistant',
        content: el.textContent?.trim() || '',
        id:      el.getAttribute('data-turn-id') || el.textContent?.slice(0, 40),
      };
    },

    /**
     * 入力欄が存在するか確認する（TIC DOM selector チェック）
     */
    isInputAlive() {
      return !!document.querySelector(SELECTORS.inputEditor);
    },

    /**
     * メインコンテンツ要素を返す（MutationObserver のターゲット）
     */
    getMainTarget() {
      return document.querySelector(SELECTORS.mainContent) || document.body;
    },
  };
})();
