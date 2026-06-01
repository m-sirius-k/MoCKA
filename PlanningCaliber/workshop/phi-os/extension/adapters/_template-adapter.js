// _template-adapter.js — 新製品向けアダプターテンプレート（Prism / Vault 等）
// このファイルをコピーして製品名を置換するだけで新 adapter を作成できる。
// TODO_188
'use strict';

import { PHI_ADAPTER } from './phi-adapter.js';
import { emit, subscribe } from '../core/event-bus.js';

// ── 製品固有設定 ─────────────────────────────────────────────────────────────
// ▼ 製品名を小文字で設定する（storage key プレフィックスになる）
const PRODUCT_NAME = 'template';

// ▼ この製品が発行するイベント種別
const EMIT_EVENTS = [
  'TEMPLATE_SYNC',
  'TEMPLATE_ACTION',
];

// ▼ この製品が購読するイベント種別
const SUBSCRIBE_EVENTS = [
  'PHI_COMMIT_DONE',
];

// ─────────────────────────────────────────────────────────────────────────────

export const TEMPLATE_ADAPTER = {
  /**
   * 製品データを PHI OS Hub に書き込む
   * @param {string} key   製品内のデータキー
   * @param {*} value
   */
  async sync(key, value) {
    await PHI_ADAPTER.write(PRODUCT_NAME, key, value);
    await emit(`${PRODUCT_NAME.toUpperCase()}_SYNC`, { key, ts: Date.now() });
  },

  /**
   * 製品データを PHI OS Hub から読み込む
   * @param {string} key
   * @param {*} defaultValue
   * @returns {Promise<*>}
   */
  async load(key, defaultValue = null) {
    return PHI_ADAPTER.read(PRODUCT_NAME, key, defaultValue);
  },

  /**
   * 製品固有のアクションを PHI OS に通知する
   * @param {string} action   アクション識別子
   * @param {object} payload
   */
  async dispatchAction(action, payload = {}) {
    await emit(`${PRODUCT_NAME.toUpperCase()}_ACTION`, { action, payload, ts: Date.now() });
  },

  /**
   * PHI OS からのコミット完了通知を受け取るフック
   * @param {Function} callback  (event) => void
   * @returns {Function} unsubscribe 関数
   */
  onCommitDone(callback) {
    return subscribe(SUBSCRIBE_EVENTS, callback);
  },

  /**
   * エラーを PHI OS 経由で MoCKA に記録する
   * エラーが製品単体で処理できない場合に使用する
   * @param {string} errorType
   * @param {string} message
   */
  async reportError(errorType, message) {
    try {
      await PHI_ADAPTER.notify('PHI_ADAPTER_ERROR', {
        product: PRODUCT_NAME,
        errorType,
        message,
        ts: Date.now(),
      });
    } catch {
      // エラー報告失敗は無視（製品動作を止めない）
    }
  },
};

// ─── 使い方 (コメント) ────────────────────────────────────────────────────────
//
// 1. このファイルを adapters/prism-adapter.js にコピーする
// 2. PRODUCT_NAME = 'prism' に変更する
// 3. EMIT_EVENTS / SUBSCRIBE_EVENTS を製品仕様に合わせて変更する
// 4. TEMPLATE_ADAPTER を PRISM_ADAPTER に改名する
// 5. 各メソッドの実装を製品ロジックに合わせてカスタマイズする
//
// PHI OS 未インストール時でも PHI_ADAPTER の fallback により
// chrome.storage.local のみで動作する（例外は吐かない）。
