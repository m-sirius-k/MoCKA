// orchestra-adapter.js — Orchestra 専用アダプター（将来実装用骨格）
'use strict';

import { PHI_ADAPTER } from './phi-adapter.js';
import { emit }        from '../core/event-bus.js';

export const ORCHESTRA_ADAPTER = {
  /**
   * Orchestra の会話データを PHI OS Hub に書き込む
   * @param {object} conversationData
   */
  async syncConversation(conversationData) {
    await PHI_ADAPTER.write('orchestra', 'conversation_latest', conversationData);
    await emit('ORCHESTRA_SYNC', { ts: Date.now() });
  },

  /**
   * PHI OS Commit完了時に Orchestra が文脈を取得するフック
   * @param {Function} callback
   * @returns {Function} unsubscribe
   */
  onCommitDone(callback) {
    const { subscribe } = require('../core/event-bus.js');
    return subscribe(['PHI_COMMIT_DONE'], callback);
  },
};
