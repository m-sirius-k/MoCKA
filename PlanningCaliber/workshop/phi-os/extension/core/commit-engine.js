// commit-engine.js — セッション終了時5点構造化保存
'use strict';

import { set, get, idbSaveCommit } from './state-store.js';
import { reportError } from '../debug/error-reporter.js';

const MAX_COMMITS = 50;

/**
 * CommitEngine — セッション内容を5点構造化してストレージに保存する
 *
 * 保存する5点:
 *   1. facts      — 新事実（ファイルパス・設定変更・新発見）
 *   2. decisions  — 新決定（採用/却下した判断とその理由）
 *   3. todos      — 残課題（未完了・ブロック中）
 *   4. tensions   — 違和感（tension/anomaly/unresolved タグ）
 *   5. next_hook  — 次回起動フック（次セッション開始時に必ず復元すべきコンテキスト）
 */
export class CommitEngine {
  /**
   * @param {string} trigger  発火理由 (UNLOAD|VISIBILITY|TURN_THRESHOLD|IDLE|MANUAL)
   */
  async commit({ trigger, ts = Date.now() }) {
    try {
      const session = await this._collectSession();

      // ターン数が少なすぎるセッションはスキップ（誤発火防止）
      if ((session.turnCount || 0) < 3 && trigger !== 'MANUAL') {
        console.log('[PHI OS CommitEngine] Skipped — turn count too low:', session.turnCount);
        return null;
      }

      const packet = {
        commit_id:  `CMT_${Date.now()}`,
        trigger,
        ts,
        facts:      this._extractFacts(session),
        decisions:  this._extractDecisions(session),
        todos:      this._extractTodos(session),
        tensions:   this._extractTensions(session),
        next_hook:  this._buildNextHook(session),
      };

      await this._save(packet);
      await set('phi_last_commit_ts', Date.now());
      console.log('[PHI OS CommitEngine] Committed:', packet.commit_id, 'trigger:', trigger);
      return packet;
    } catch (e) {
      await reportError({ type: 'COMMIT_ERROR', message: e.message, trigger, ts: Date.now() });
      throw e;
    }
  }

  _extractFacts(session) {
    // ファイルパスを検出: Windows/Unix/相対パス
    const PATH_RE = /([A-Za-z]:\\[\w\\.\-/]+|\/[\w/.\-]{4,}|\.\/[\w/.\-]+)/g;
    return [...new Set((session.text || '').match(PATH_RE) || [])].slice(0, 20);
  }

  _extractDecisions(session) {
    const DEC_PATTERNS = [
      /[「『](.{5,60})[」』](?:で|に|として)(?:決定|確定|採用|却下)/g,
      /(.{5,60})(?:にした|で行く|で確定|を採用|を却下)/g,
    ];
    const decisions = [];
    for (const re of DEC_PATTERNS) {
      let m;
      while ((m = re.exec(session.text || '')) !== null) {
        decisions.push(m[1]);
      }
    }
    return [...new Set(decisions)].slice(0, 10);
  }

  _extractTodos(session) {
    // [RELAY_TODO] タグ最優先
    const TAGGED = /\[RELAY_TODO\]\s*(.+)/g;
    const tagged = [];
    let m;
    while ((m = TAGGED.exec(session.text || '')) !== null) {
      tagged.push(m[1].trim());
    }

    // Relay の logbook から直接取得した todos も合わせる
    const existing = session.todos || [];
    return [...new Set([...tagged, ...existing.map(t => t.text || t)])].slice(0, 15);
  }

  _extractTensions(session) {
    const TENSION_RE = /(?:なぜ|どうして|おかしい|違和感|うまくいかない|意味がわからん|tension|anomaly)(.{5,50})/g;
    const tensions = [];
    let m;
    while ((m = TENSION_RE.exec(session.text || '')) !== null) {
      tensions.push({ text: m[0], tag: 'tension' });
    }
    return tensions.slice(0, 5);
  }

  _buildNextHook(session) {
    return {
      last_file:     session.lastFilePath   || null,
      last_decision: session.decisions?.[0]  || null,
      pending_todos: (session.todos || []).slice(0, 3).map(t => t.text || t),
    };
  }

  async _collectSession() {
    try {
      // Relay のストレージからセッションデータを取得
      const stored = await chrome.storage.local.get([
        'relay_current',
        'relay_todos',
        'relay_logbook_current',
      ]);

      const current  = stored['relay_current']          || {};
      const todos    = stored['relay_todos']             || [];
      const logbook  = stored['relay_logbook_current']   || {};

      return {
        text:         logbook.text     || '',
        turnCount:    current.turn_count || 0,
        todos:        todos.filter(t => t.status === 'active'),
        decisions:    current.decisions  || [],
        lastFilePath: logbook.last_file  || null,
      };
    } catch (e) {
      await reportError({ type: 'COLLECT_SESSION_ERROR', message: e.message, ts: Date.now() });
      return { text: '', turnCount: 0, todos: [], decisions: [], lastFilePath: null };
    }
  }

  async _save(packet) {
    const key = `phi_commit_${packet.commit_id}`;
    await set(key, packet);

    // コミットインデックスを更新（最新50件）
    const index = await get('phi_commit_index', []);
    index.unshift(packet.commit_id);
    if (index.length > MAX_COMMITS) index.pop();
    await set('phi_commit_index', index);

    // IndexedDB Hubにも保存（content.js内での呼び出し時のみ有効）
    try {
      await idbSaveCommit(packet);
    } catch {
      // IndexedDB が使えない環境（background.js等）では無視
    }
  }
}
