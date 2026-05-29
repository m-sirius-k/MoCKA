// auto-trigger.js — セッション終了を構造的に検知してcommit-engineを自動発火
'use strict';

import { CommitEngine } from './commit-engine.js';
import { reportError }  from '../debug/error-reporter.js';

/**
 * AutoTrigger — 5つのトリガーでCommitを自動発火する
 *
 * 発火条件（優先順）:
 *   1. UNLOAD        — ウィンドウ/タブ閉じる（beforeunload）
 *   2. VISIBILITY    — タブ切り替え（visibilitychange → hidden）
 *   3. TURN_THRESHOLD— 20ターン経過
 *   4. IDLE          — 5分間操作なし
 *   5. MANUAL        — 手動ボタン（commit()を外部から直接呼ぶ）
 *
 * 重複防止:
 *   - 前回Commit時刻から DEDUP_MS 以内は再発火しない
 *   - commitInProgress フラグでネスト呼び出し防止
 */
export class AutoTrigger {
  constructor() {
    this.engine     = new CommitEngine();
    this.DEDUP_MS   = 300000;   // 5分
    this.IDLE_MS    = 300000;   // 5分アイドル
    this.TURN_LIMIT = 20;

    this.inProgress  = false;
    this._idleTimer  = null;
    this._turnCount  = 0;
    this._initialized = false;
  }

  init() {
    if (this._initialized) return;
    this._initialized = true;

    // Trigger 1: beforeunload（Chrome拡張では補助的）
    window.addEventListener('beforeunload', () => this.fire('UNLOAD'));

    // Trigger 2: visibilitychange
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) this.fire('VISIBILITY');
    });

    // Trigger 4: アイドル検知（アクティビティでリセット）
    ['click', 'keydown', 'scroll'].forEach(ev => {
      document.addEventListener(ev, () => this._resetIdle(), { passive: true });
    });
    this._resetIdle();

    console.log('[PHI OS AutoTrigger] Initialized');
  }

  /** ターンが完了するたびにRelayのcontent.jsから呼び出す */
  onTurn() {
    this._turnCount++;
    if (this._turnCount >= this.TURN_LIMIT) {
      this._turnCount = 0;
      this.fire('TURN_THRESHOLD');
    }
  }

  /** 外部から手動でコミットをトリガーする */
  async manualCommit() {
    return this.fire('MANUAL', true);
  }

  /**
   * コミットを発火する
   * @param {string} reason  発火理由
   * @param {boolean} forceSkipDedup  重複チェックを無視する（手動コミット用）
   */
  async fire(reason, forceSkipDedup = false) {
    if (this.inProgress) return null;

    if (!forceSkipDedup) {
      try {
        const stored = await chrome.storage.local.get('phi_last_commit_ts');
        const lastTs = stored['phi_last_commit_ts'] || 0;
        if (Date.now() - lastTs < this.DEDUP_MS) {
          console.log('[PHI OS AutoTrigger] Skipped (dedup):', reason);
          return null;
        }
      } catch (e) {
        await reportError({ type: 'TRIGGER_DEDUP_ERROR', message: e.message, ts: Date.now() });
      }
    }

    this.inProgress = true;
    let result = null;
    try {
      result = await this.engine.commit({ trigger: reason, ts: Date.now() });
      // コミット完了をUIに通知
      chrome.runtime.sendMessage({ type: 'PHI_COMMIT_DONE', trigger: reason }).catch(() => {});
    } catch (e) {
      await reportError({ type: 'AUTO_TRIGGER_COMMIT_ERROR', message: e.message, reason, ts: Date.now() });
    } finally {
      this.inProgress = false;
    }
    return result;
  }

  _resetIdle() {
    clearTimeout(this._idleTimer);
    this._idleTimer = setTimeout(() => this.fire('IDLE'), this.IDLE_MS);
  }

  destroy() {
    clearTimeout(this._idleTimer);
  }
}
