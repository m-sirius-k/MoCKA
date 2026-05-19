/**
 * Relay — relay-state.js
 * @version 3.2.0
 * @description 全モジュールが参照する共有状態の唯一の真実源。
 *              このファイルを manifest content_scripts[].js の最初に注入する。
 *
 * Purpose  : Relay.state / Relay.config / Relay.services の初期化
 * Owns     : globalThis.__RELAY__ の定義
 * Must not : DOM操作・chrome API・localStorage・副作用を持たない
 * Inputs   : なし（最初に実行される）
 * Outputs  : globalThis.__RELAY__
 *
 * Known traps:
 *   - このファイルが2回実行されても if(__RELAY__) return で安全に冪等化している
 *   - 他ファイルは必ず globalThis.__RELAY__ 経由でアクセスすること
 *   - Relay.state を直接代入せず、必ず Relay.state.xxx = value で更新する
 */

(() => {
  'use strict';

  // 二重初期化防止（SPA遷移・HMR対策）
  if (globalThis.__RELAY__) return;

  const Relay = {

    // ─── 共有状態 ────────────────────────────────────────────────────────────
    state: {
      // アシスタント出力バッファ
      lastAssistantText       : '',   // DOM から取得した最新テキスト（生）
      lastStableAssistantText : '',   // streamIdleMs 後に確定した安定テキスト
      lastUserText            : '',   // 最新のユーザー入力テキスト

      // ターン管理
      turnCount      : 0,
      warningShown   : false,

      // Observer ハンドル（多重登録防止のため一元管理）
      observers: {
        assistant : null,  // MutationObserver instance or null
        user      : null,
        badge     : null,
      },

      // タイマーハンドル
      streamIdleTimer : null,
      badgeTimer      : null,

      // セッション
      sessionId  : null,   // 起動時に crypto.randomUUID() で設定
      sessionUrl : '',

      // Relay システム状態
      initialized   : false,
      lastSavedHash : '',   // 重複保存防止
    },

    // ─── 設定 ────────────────────────────────────────────────────────────────
    config: {
      streamIdleMs       : 1200,   // テキスト安定判定（ms）
      minTodoLen         : 8,      // TODO候補の最小文字数
      turnWarningAt      : 20,     // ターン警告を出すターン数
      todoScoreThreshold : 1,      // TODO保存スコア閾値
      maxTodosPerSession : 50,     // セッションあたりTODO最大件数
      badgeUpdateMs      : 2000,   // バッジ更新間隔
      selectorRetryMs    : 500,    // セレクタ再試行間隔
      selectorMaxRetry   : 10,     // セレクタ最大再試行回数
    },

    // ─── サービスレジストリ（各モジュールが自己登録する）─────────────────────
    services: {
      dom        : null,   // relay-dom.js が設定
      watchers   : null,   // relay-watchers.js が設定
      logbook    : null,   // relay-logbook.js が設定
      ui         : null,   // relay-ui.js が設定
      handoff    : null,   // relay-main.js が設定
    },

    // ─── ユーティリティ ───────────────────────────────────────────────────────
    utils: {
      /**
       * FNV-1a 非暗号ハッシュ（重複検出用）
       */
      hash(str = '') {
        let h = 0x811c9dc5;
        for (let i = 0; i < str.length; i++) {
          h ^= str.charCodeAt(i);
          h = (h * 0x01000193) >>> 0;
        }
        return h.toString(16).padStart(8, '0');
      },

      /**
       * デバウンス関数
       */
      debounce(fn, ms) {
        let timer = null;
        return (...args) => {
          clearTimeout(timer);
          timer = setTimeout(() => fn(...args), ms);
        };
      },

      /**
       * タイムスタンプ
       */
      now() { return new Date().toISOString(); },

      /**
       * UUID生成（フォールバック付き）
       */
      uuid() {
        if (typeof crypto !== 'undefined' && crypto.randomUUID) {
          return crypto.randomUUID();
        }
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
          const r = Math.random() * 16 | 0;
          return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
        });
      },
    },

  };

  // セッションIDを初期化
  Relay.state.sessionId = Relay.utils.uuid();

  // グローバルに公開（content script 間の唯一の共有面）
  globalThis.__RELAY__ = Relay;

  console.info('[Relay] relay-state.js initialized. session:', Relay.state.sessionId);

})();
