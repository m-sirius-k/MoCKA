// restore-engine.js — Restore Packet 生成と claude.ai 入力欄注入
'use strict';

import { get, idbGetRecentCommits } from './state-store.js';
import { reportError }              from '../debug/error-reporter.js';
import { getLang }                  from './i18n.js';

const MAX_CHARS = 3000;

const HEADERS = {
  ja: {
    title:     '【前回セッション復元】',
    facts:     '📁 ファイル',
    decisions: '✅ 決定事項',
    todos:     '📋 TODO',
    tensions:  '⚠️ 違和感',
    next:      '➡️ 次のアクション',
    footer:    '上記を踏まえて作業を継続してください。',
  },
  en: {
    title:     '[Session Restore]',
    facts:     '📁 Files',
    decisions: '✅ Decisions',
    todos:     '📋 TODOs',
    tensions:  '⚠️ Tensions',
    next:      '➡️ Next action',
    footer:    'Please continue work with the above context.',
  },
  zh: {
    title:     '【上次会话恢复】',
    facts:     '📁 文件',
    decisions: '✅ 决策',
    todos:     '📋 待办',
    tensions:  '⚠️ 疑虑',
    next:      '➡️ 下一步',
    footer:    '请基于以上内容继续工作。',
  },
  ko: {
    title:     '【이전 세션 복원】',
    facts:     '📁 파일',
    decisions: '✅ 결정사항',
    todos:     '📋 할일',
    tensions:  '⚠️ 의문점',
    next:      '➡️ 다음 작업',
    footer:    '위 내용을 바탕으로 작업을 계속해주세요.',
  },
  es: {
    title:     '[Restaurar sesión]',
    facts:     '📁 Archivos',
    decisions: '✅ Decisiones',
    todos:     '📋 Tareas',
    tensions:  '⚠️ Dudas',
    next:      '➡️ Siguiente',
    footer:    'Por favor continúa el trabajo con el contexto anterior.',
  },
};

export class RestoreEngine {
  /**
   * Restore Packet 文字列を生成する
   * @returns {Promise<string|null>}
   */
  async buildPacket() {
    try {
      const commits = await this._loadRecentCommits(5);
      if (!commits.length) return null;

      const scored  = this._scoreCommits(commits);
      return this._format(scored);
    } catch (e) {
      await reportError({ type: 'RESTORE_BUILD_ERROR', message: e.message, ts: Date.now() });
      return null;
    }
  }

  /**
   * claude.ai の新規チャット入力欄に Restore Packet を注入する
   * MutationObserver で入力欄の出現を待ってから注入する
   * @returns {Promise<boolean>}
   */
  async inject() {
    try {
      const packet = await this.buildPacket();
      if (!packet) return false;

      const input = await this._waitForInput(5000);
      if (!input) {
        await reportError({ type: 'RESTORE_NO_INPUT', message: 'Input element not found', ts: Date.now() });
        return false;
      }

      this._setInputValue(input, packet);
      console.log('[PHI OS RestoreEngine] Injected', packet.length, 'chars');
      return true;
    } catch (e) {
      await reportError({ type: 'RESTORE_INJECT_ERROR', message: e.message, ts: Date.now() });
      return false;
    }
  }

  // ─── スコアリング ──────────────────────────────────────────────────────────

  _scoreCommits(commits) {
    return commits
      .map((c, idx) => ({
        ...c,
        score: (
          (1 - idx * 0.15)                           * 0.35 +  // recency
          (c.decisions?.length > 0 ? 1 : 0)          * 0.30 +  // causality
          ((c.facts?.length || 0) / 20)              * 0.20 +  // frequency
          (c.tensions?.length > 0 ? 1 : 0)           * 0.15    // tension
        ),
      }))
      .sort((a, b) => b.score - a.score);
  }

  // ─── フォーマット ──────────────────────────────────────────────────────────

  _format(commits) {
    const lang = getLang() || 'ja';
    const h    = HEADERS[lang] || HEADERS['en'];
    const lines = [h.title, '─'.repeat(36), ''];

    for (const c of commits) {
      const date = new Date(c.ts);
      const ds   = `${date.getMonth() + 1}/${date.getDate()} ${String(date.getHours()).padStart(2,'0')}:${String(date.getMinutes()).padStart(2,'0')}`;
      lines.push(`[${ds}] ${c.trigger || '?'}`);

      if (c.facts?.length) {
        lines.push(`  ${h.facts}:`);
        c.facts.slice(0, 5).forEach(f => lines.push(`    ${f}`));
      }
      if (c.decisions?.length) {
        lines.push(`  ${h.decisions}:`);
        c.decisions.slice(0, 3).forEach(d => lines.push(`    - ${d}`));
      }
      if (c.todos?.length) {
        lines.push(`  ${h.todos}:`);
        c.todos.slice(0, 5).forEach(t => lines.push(`    □ ${typeof t === 'string' ? t : t.text}`));
      }
      if (c.tensions?.length) {
        lines.push(`  ${h.tensions}:`);
        c.tensions.slice(0, 2).forEach(t => lines.push(`    ⚠ ${t.text}`));
      }
      if (c.next_hook?.pending_todos?.length) {
        lines.push(`  ${h.next}:`);
        c.next_hook.pending_todos.forEach(t => lines.push(`    → ${t}`));
      }
      lines.push('');
    }

    lines.push('─'.repeat(36));
    lines.push(h.footer);

    // 3000文字上限で切り詰める
    let result = lines.join('\n');
    if (result.length > MAX_CHARS) {
      result = result.slice(0, MAX_CHARS - 3) + '...';
    }
    return result;
  }

  // ─── ストレージ ────────────────────────────────────────────────────────────

  async _loadRecentCommits(limit) {
    // IndexedDB 優先
    try {
      const idbCommits = await idbGetRecentCommits(limit);
      if (idbCommits.length) return idbCommits;
    } catch {
      // fall through to storage.local
    }

    // chrome.storage.local フォールバック
    const index = await get('phi_commit_index', []);
    const commits = [];
    for (const id of index.slice(0, limit)) {
      const c = await get(`phi_commit_${id}`);
      if (c) commits.push(c);
    }
    return commits;
  }

  // ─── DOM操作 ───────────────────────────────────────────────────────────────

  _waitForInput(timeout) {
    return new Promise(resolve => {
      const el = this._findInput();
      if (el) { resolve(el); return; }

      // MutationObserver で出現を待つ
      const observer = new MutationObserver(() => {
        const found = this._findInput();
        if (found) {
          observer.disconnect();
          clearTimeout(timer);
          resolve(found);
        }
      });
      observer.observe(document.body, { childList: true, subtree: true });

      const timer = setTimeout(() => {
        observer.disconnect();
        resolve(this._findInput() || null);
      }, timeout);
    });
  }

  _findInput() {
    const selectors = [
      'div[contenteditable="true"][data-testid="composer-input"]',
      'div[contenteditable="true"].ProseMirror',
      'div[contenteditable="true"]',
    ];
    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el) return el;
    }
    return null;
  }

  _setInputValue(el, text) {
    el.focus();
    const sel = window.getSelection();
    const rng = document.createRange();
    rng.selectNodeContents(el);
    sel.removeAllRanges();
    sel.addRange(rng);

    const ok = document.execCommand('insertText', false, text);
    if (!ok) {
      el.innerText = text;
      el.dispatchEvent(new InputEvent('input', { bubbles: true, cancelable: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    }
  }
}
