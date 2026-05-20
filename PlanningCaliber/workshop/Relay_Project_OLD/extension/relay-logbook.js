/**
 * Relay — relay-logbook.js
 * @version 3.4.0
 * @description TODO抽出・タグ処理・chrome.storage.local 永続化。
 *
 * Purpose  : 安定テキストから TODO を4段階パイプラインで抽出・保存・管理
 * Owns     : extractTodos / saveTodo / getTodos / updateStatus / deleteTodo / archiveDone
 * Must not : DOM操作・MutationObserver・state.lastAssistantText への書き込み
 * Inputs   : Relay.state.lastStableAssistantText（watchers経由で受け取る）
 * Outputs  : chrome.storage.local['relay_todos']
 *
 * v3.4.0 変更点:
 *   - schema_ver 1→2: status ('未着手'|'進行中'|'完了') / priority ('低'|'中'|'高') 追加
 *   - updateStatus(id, newStatus) 追加
 *   - deleteTodo(id) 追加（relay-main.js の _saveAllTodos 依存を解消）
 *   - getTodos() で旧スキーマ (done: boolean) を自動正規化
 *   - extractTodos() でスコアから priority を自動付与
 *   - archiveDone() で新旧スキーマ両対応
 *
 * Pipeline:
 *   Stage 1: 前処理  — コードブロック・インライン・テーブル除去
 *   Stage 2: フィルタ — コード行・記号密度・極端短文を除外
 *   Stage 3: スコア  — 命令動詞・TODO接頭辞でスコアリング
 *   Stage 4: 保存   — [RELAY_TODO]タグ最優先・閾値以上のみ保存
 */

(() => {
  'use strict';

  const Relay = globalThis.__RELAY__;
  if (!Relay) { console.error('[Relay] relay-logbook.js: __RELAY__ not found'); return; }

  const STORAGE_KEY = 'relay_todos';
  const SCHEMA_VER  = 2;

  // ─── Stage 1: 前処理 ─────────────────────────────────────────────────────────

  function _preprocess(raw) {
    return raw
      .replace(/```[\s\S]*?```/g, '\n')
      .replace(/`[^`\n]+`/g, '')
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
      if (line.length < 8)                 return false;
      if (_CODE_PATTERN.test(line))        return false;
      if (_SYMBOL_PATTERN.test(line))      return false;
      if (/^\[\[Prototype\]\]/.test(line)) return false;
      return true;
    });
  }

  // ─── Stage 3: スコアリング ────────────────────────────────────────────────────

  function _score(line) {
    let score = 0;
    if (/^(todo|to[\s-]do|next|action|follow[\s-]?up|やること|次にやること|次の?アクション)[:：\-\s]/i.test(line)) score += 3;
    if (/^(fix|add|check|review|test|refactor|implement|verify|document|update|remove|create|write|confirm|ensure|make)/i.test(line)) score += 3;
    if (/^(調査|修正|確認|追加|実装|作成|更新|削除|検証|テスト|改善|整理|設計|検討|対応)/.test(line)) score += 3;
    if (/\b(してください|お願い|要確認|要修正|要追加|ください)\b/.test(line)) score += 2;
    const camelCount = (line.match(/[a-z][A-Z]/g) ?? []).length;
    if (camelCount >= 2) score -= 4;
    if ((line.match(/[\d\W]/g) ?? []).length > line.length * 0.5) score -= 2;
    return score;
  }

  // スコアから priority を導出
  function _priorityFromScore(score) {
    if (score >= 5) return '高';
    if (score >= 3) return '中';
    return '低';
  }

  // ─── [RELAY_TODO] タグ抽出（最優先経路）─────────────────────────────────────

  function _extractTagged(text) {
    const results = [];
    const re = /\[RELAY_TODO\]([\s\S]*?)\[\/RELAY_TODO\]/g;
    let m;
    while ((m = re.exec(text)) !== null) {
      const content = m[1].trim();
      if (content.length >= Relay.config.minTodoLen) {
        results.push({ content, source: 'tag', score: 99, priority: '高' });
      }
    }
    return results;
  }

  // ─── Stage 4: パイプライン統合 ────────────────────────────────────────────────

  function extractTodos(text) {
    if (!text || text.length < Relay.config.minTodoLen) return [];
    const tagged   = _extractTagged(text);
    const lines    = _preprocess(text);
    const filtered = _filterLines(lines);
    const scored   = filtered
      .map(line => {
        const score = _score(line);
        return { content: line, source: 'auto', score, priority: _priorityFromScore(score) };
      })
      .filter(item => item.score >= Relay.config.todoScoreThreshold);
    return [...tagged, ...scored];
  }

  // ─── 旧スキーマ正規化（done: boolean → status: string）───────────────────────
  // 保存済みレコードに status がない場合に補完する。storage は書き換えない。

  function _normalize(record) {
    if (record.status) return record;
    return {
      ...record,
      status    : record.done ? '完了' : '未着手',
      priority  : record.priority || '中',
      schema_ver: SCHEMA_VER,
    };
  }

  // ─── レコード生成 ─────────────────────────────────────────────────────────────

  function _makeRecord(content, source = 'auto', priority = '中') {
    return {
      id         : `todo_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 5)}`,
      content,
      source,
      session_id : Relay.state.sessionId,
      created_at : new Date().toISOString(),
      status     : '未着手',
      priority,
      archived   : false,
      schema_ver : SCHEMA_VER,
    };
  }

  // ─── storage I/O ─────────────────────────────────────────────────────────────

  function _load() {
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

  function _save(todos) {
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

  // ─── 保存 ─────────────────────────────────────────────────────────────────────

  async function saveTodo(content, source = 'auto', priority = '中') {
    if (!content || content.length < Relay.config.minTodoLen) return null;

    const hash  = Relay.utils.hash(content);
    const todos = await _load();

    const isDuplicate = todos.some(t =>
      t.session_id === Relay.state.sessionId &&
      Relay.utils.hash(t.content) === hash
    );
    if (isDuplicate) return null;

    const sessionTodos = todos.filter(t => t.session_id === Relay.state.sessionId);
    if (sessionTodos.length >= Relay.config.maxTodosPerSession) return null;

    const record = _makeRecord(content, source, priority);
    todos.push(record);
    await _save(todos);
    return record;
  }

  async function processStableText(text) {
    const candidates = extractTodos(text);
    const saved = [];
    for (const item of candidates) {
      const rec = await saveTodo(item.content, item.source, item.priority);
      if (rec) saved.push(rec);
    }
    Relay.state.lastSavedHash = Relay.utils.hash(text);
    return saved;
  }

  // ─── 取得（旧スキーマ自動正規化付き）────────────────────────────────────────

  async function getTodos({ sessionOnly = false, includeArchived = false } = {}) {
    const todos = await _load();
    return todos
      .map(_normalize)
      .filter(t => {
        if (!includeArchived && t.archived) return false;
        if (sessionOnly && t.session_id !== Relay.state.sessionId) return false;
        return true;
      });
  }

  // ─── ステータス更新 ───────────────────────────────────────────────────────────

  async function updateStatus(id, newStatus) {
    const todos = await _load();
    const t = todos.find(t => t.id === id);
    if (!t) return false;
    t.status = newStatus;
    if (newStatus === '完了') t.completed_at = new Date().toISOString();
    // 旧フィールドも同期（後方互換）
    t.done = newStatus === '完了';
    return _save(todos);
  }

  // 旧 API 後方互換
  async function toggleDone(id) {
    const todos = await _load();
    const t = todos.find(t => t.id === id);
    if (!t) return false;
    const current = _normalize(t).status;
    return updateStatus(id, current === '完了' ? '未着手' : '完了');
  }

  // ─── 削除 ─────────────────────────────────────────────────────────────────────

  async function deleteTodo(id) {
    const todos = await _load();
    const filtered = todos.filter(t => t.id !== id);
    if (filtered.length === todos.length) return false;
    return _save(filtered);
  }

  // ─── 完了済みをアーカイブ ─────────────────────────────────────────────────────

  async function archiveDone() {
    const todos = await _load();
    let changed = false;
    todos.forEach(t => {
      const normalized = _normalize(t);
      if (normalized.status === '完了' && !t.archived) {
        t.archived = true;
        changed = true;
      }
    });
    if (changed) await _save(todos);
    return changed;
  }

  // ─── サービスとして登録 ───────────────────────────────────────────────────────
  // NOTE: watchers 接続は relay-main.js の _connectAllCallbacks() で行う。

  Relay.services.logbook = Object.freeze({
    extractTodos,
    processStableText,
    saveTodo,
    getTodos,
    updateStatus,
    toggleDone,
    deleteTodo,
    archiveDone,
  });

  console.info('[Relay] relay-logbook.js registered. v3.4.0');

})();
