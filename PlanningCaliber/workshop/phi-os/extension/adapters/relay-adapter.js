// relay-adapter.js — Relay 専用アダプター
'use strict';

import { PHI_ADAPTER } from './phi-adapter.js';
import { emit }        from '../core/event-bus.js';

export const RELAY_ADAPTER = {
  /**
   * Relay のセッションデータを PHI OS Hub に書き込む
   * @param {object} sessionData
   */
  async syncSession(sessionData) {
    await PHI_ADAPTER.write('relay', 'session_latest', sessionData);
    await emit('RELAY_SESSION_SYNC', { ts: Date.now() });
  },

  /**
   * Relay の TODO リストを PHI OS Hub に書き込む
   * @param {Array} todos
   */
  async syncTodos(todos) {
    await PHI_ADAPTER.write('relay', 'todos_latest', todos);
  },

  /**
   * PHI OS のコミット完了通知を Relay が受け取るためのフック登録
   * @param {Function} callback
   * @returns {Function} unsubscribe
   */
  onCommitDone(callback) {
    const { subscribe } = require('../core/event-bus.js');
    return subscribe(['PHI_COMMIT_DONE'], callback);
  },
};
