/**
 * Relay — relay-logbook.js
 * @version 3.2.0
 * @description TODO抽出・タグ処理・chrome.storage.local 永続化。
 *
 * Purpose  : 安定テキストから TODO を4段階パイプラインで抽出・保存・管理
 * Owns     : extractTodos / saveTodo / getTodos / archiveDone
 * Must not : DOM操作・MutationObserver・state.lastAssistantText への書き込み
 * Inputs   : Relay.state.lastStableAssistantText（watchers経由で受け取る）
 * Outputs  : chrome.storage.local['relay_todos']
 *
 * Pipeline:
 *   Stage 1: 前処理  — コードブロック・インライン・テーブル除去
 *   Stage 2: フィルタ — コード行・記号密度・極端短文を除外
 *   Stage 3: スコア  — 命令動詞・TODO接頭辞でスコアリング
 *   Stage 4: 保存   — [RELAY_TODO]タグ最優先・閾値以上のみ保存
 *
 * Known traps:
 *   - [RELAY_TODO]...[/RELAY_TODO] は明示入力として別経路・スコア無視で保存
 *   - 同一 hash のTODOは重複保存しない
 *   - storage への書き込みは必ず try/catch で囲む
 */

(() => {
  'use strict';

  const Relay = globalThis.__RELAY__;
  if (!Relay) { console.error('[Relay] relay-logbook.js: __RELAY__ not found'); return; }

  const STORAGE_KEY = 'relay_todos';
  const SCHEMA_VER  = 1;

  // ─── Stage 1: 前処理 ─────────────────────────────────────────────────────────

  function _preprocess(raw) {
    return raw
      // コードフェンス除去
      .replace(/```[\s\S]*?```/g, '\n')
      // インラインコード除去
      .replace(/`[^`\n]+`/g, '')
      // Markdown テーブル行除去
      .split('\n')
      .map(s => s.trim())
      .filter(Boolean)
      .filter(line => !/^\|.*\|$/.test(line))
      .filter(line => !/^[\-\|\s:]+$/.test(line));
  }

  // ─── Stage 2: フィルタ ────────────────────────────────────────────────────────

  const _CODE_PATTERN = /[{};]|=>|\b(const|let|var|function|return|map|filter|join|import|export|class|async|await|typeof|instanceof)\b/;
  const _SYMBOL_PATTERN = /^[\W\d_]{4,}$/;

  function _filterLines(lines) {
    return lines.filter(line => {
      if (line.length < 8)               return false;   // 短すぎる
      if (_CODE_PATTERN.test(line))      return false;   // コード行
      if (_SYMBOL_PATTERN.test(line))    return false;   // 記号のみ
      if (/^\[\[Prototype\]\]/.test(line)) return false; // デバッグ出力
      return true;
    });
  }

  // ─── Stage 3: スコアリング ────────────────────────────────────────────────────

  function _score(line) {
    let score = 0;

    // TODO接頭辞
    if (/^(todo|to[\s-]do|next|action|follow[\s-]?up|やること|次にやること|次の?アクション)[:：\-\s]/i.test(line)) score += 3;

    // 命令動詞で始まる行（英語）
    if (/^(fix|add|check|review|test|refactor|implement|verify|document|update|remove|create|write|confirm|ensure|make)/i.test(line)) score += 3;

    // 命令動詞で始まる行（日本語）
    if (/^(調査|修正|確認|追加|実装|作成|更新|削除|検証|テスト|改善|整理|設計|検討|対応)/.test(line)) score += 3;

    // 依頼表現
    if (/\b(してください|お願い|要確認|要修正|要追加|ください)\b/.test(line)) score += 2;

    // キャメルケース多め → コード片の可能性
    const camelCount = (line.match(/[a-z][A-Z]/g) ?? []).length;
    if (camelCount >= 2) score -= 4;

    // 数字・記号が多い
    if ((line.match(/[\d\W]/g) ?? []).length > line.length * 0.5) score -= 2;

    return score;
  }

  // ─── [RELAY_TODO] タグ抽出（最優先経路）─────────────────────────────────────

  function _extractTagged(text) {
    const results = [];
    const re = /\[RELAY_TODO\]([\s\S]*?)\[\/RELAY_TODO\]/g;
    let m;
    while ((m = re.exec(text)) !== null) {
      const content = m[1].trim();
      if (content.length >= Relay.config.minTodoLen) {
        results.push({ content, source: 'tag', score: 99 });
      }
    }
    return results;
  }

  // ─── Stage 4: パイプライン統合 ────────────────────────────────────────────────

  /**
   * テキストからTODO候補を抽出する。
   * @param {string} text アシスタント安定テキスト
   * @returns {{ content: string, source: string, score: number }[]}
   */
  function extractTodos(text) {
    if (!text || text.length < Relay.config.minTodoLen) return [];

    // [RELAY_TODO]タグは別経路（最優先）
    const tagged = _extractTagged(text);

    // 通常パイプライン
    const lines   = _preprocess(text);
    const filtered = _filterLines(lines);
    const scored  = filtered
      .map(line => ({ content: line, source: 'auto', score: _score(line) }))
      .filter(item => item.score >= Relay.config.todoScoreThreshold);

    return [...tagged, ...scored];
  }

  // ─── 永続化 ───────────────────────────────────────────────────────────────────

  function _makeRecord(content, source = 'auto') {
    return {
      id         : `todo_${Date.now().toString(36)}_${Math.random().toString(36).slice(2,5)}`,
      content,
      source,
      session_id : Relay.state.sessionId,
      created_at : new Date().toISOString(),
      done       : false,
      archived   : false,
      schema_ver : SCHEMA_VER,
    };
  }

  async function _load() {
    return new Promise(resolve => {
      try {
        chrome.storage.local.get(STORAGE_KEY, res => {
          if (chrome.runtime.lastError) { resolve([]); return; }
          const data = res[STORAGE_KEY];
          resolve(Array.isArray(data) ? data : []);
        });
      } catch (_) { resolve([]); }
    });
  }

  async function _save(todos) {
    return new Promise(resolve => {
      try {
        chrome.storage.local.set({ [STORAGE_KEY]: todos }, () => {
          if (chrome.runtime.lastError) {
            console.warn('[Relay] logbook save error:', chrome.runtime.lastError.message);
            resolve(false); return;
          }
          resolve(true);
        });
      } catch (_) { resolve(false); }
    });
  }

  /**
   * TODO を保存する。重複は hash で検出してスキップ。
   */
  async function saveTodo(content, source = 'auto') {
    if (!content || content.length < Relay.config.minTodoLen) return null;

    const hash  = Relay.utils.hash(content);
    const todos = await _load();

    // セッション内での重複チェック
    const isDuplicate = todos.some(t =>
      t.session_id === Relay.state.sessionId &&
      Relay.utils.hash(t.content) === hash
    );
    if (isDuplicate) return null;

    // 最大件数チェック
    const sessionTodos = todos.filter(t => t.session_id === Relay.state.sessionId);
    if (sessionTodos.length >= Relay.config.maxTodosPerSession) return null;

    const record = _makeRecord(content, source);
    todos.push(record);
    await _save(todos);
    return record;
  }

  /**
   * 安定テキストからTODOを一括抽出・保存する。
   * watchers の onStableAssistant コールバックから呼ぶ。
   */
  async function processStableText(text) {
    const candidates = extractTodos(text);
    const saved = [];
    for (const item of candidates) {
      const rec = await saveTodo(item.content, item.source);
      if (rec) saved.push(rec);
    }

    // hash 記録（同じ安定テキストを再処理しない）
    Relay.state.lastSavedHash = Relay.utils.hash(text);

    return saved;
  }

  /**
   * 全TODOを返す。
   */
  async function getTodos({ sessionOnly = false, includeArchived = false } = {}) {
    const todos = await _load();
    return todos.filter(t => {
      if (!includeArchived && t.archived) return false;
      if (sessionOnly && t.session_id !== Relay.state.sessionId) return false;
      return true;
    });
  }

  /**
   * TODO を完了/未完了にする。
   */
  async function toggleDone(id) {
    const todos = await _load();
    const t = todos.find(t => t.id === id);
    if (!t) return false;
    t.done = !t.done;
    return await _save(todos);
  }

  /**
   * 完了済みTODOをアーカイブする。
   */
  async function archiveDone() {
    const todos = await _load();
    let changed = false;
    todos.forEach(t => { if (t.done && !t.archived) { t.archived = true; changed = true; } });
    if (changed) await _save(todos);
    return changed;
  }

  // ─── サービスとして登録 ───────────────────────────────────────────────────────

  Relay.services.logbook = Object.freeze({
    extractTodos,
    processStableText,
    saveTodo,
    getTodos,
    toggleDone,
    archiveDone,
  });

  // watchers の onStableAssistant に自動接続
  // （watchers より後に読み込まれることが保証されていれば即接続）
  const _connectWatchers = () => {
    if (!Relay.services.watchers) return;
    Relay.services.watchers.on('onStableAssistant', text => {
      processStableText(text).then(saved => {
        if (saved.length > 0) {
          console.info('[Relay] logbook: saved', saved.length, 'TODOs');
          Relay.services.ui?.refreshBadge?.();
        }
      });
    });
  };

  // main.js から呼ぶか、DOM ready 後に自動接続
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', _connectWatchers);
  } else {
    _connectWatchers();
  }

  console.info('[Relay] relay-logbook.js registered.');

})();
