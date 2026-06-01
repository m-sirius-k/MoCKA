// relay-logbook.js — TODO 抽出・引き継ぎログ管理
// Task 3: LB_003 修正済み — コードブロック・記号行・短文の誤抽出を防ぐ4段階パイプライン
'use strict';

const STORAGE_KEY_LOGBOOK = 'relay_logbook';
const STORAGE_KEY_TODOS   = 'relay_todos';

// ─── TODO 抽出パイプライン（4段階）────────────────────────────────────────────

/**
 * Stage 1: コードブロックを除外したテキストを返す
 */
function removeCodeBlocks(text) {
  // バッククォートトリプルのコードブロック
  return text.replace(/```[\s\S]*?```/g, '')
             .replace(/`[^`\n]+`/g, '');
}

/**
 * Stage 2: 候補行を抽出する（最低限の長さ・TODO パターン）
 */
function extractCandidateLines(text) {
  return text
    .split('\n')
    .map(l => l.trim())
    .filter(l => l.length >= 10);  // 短文除外（10文字未満）
}

/**
 * Stage 3: 記号行・コード行フィルター（LB_003 追加フィルター）
 * 行末が } ; ) の行はコードの閉じ括弧とみなして除外する
 */
function filterCodeLines(lines) {
  return lines.filter(l => {
    // 行末がコード終端文字 → 除外
    if (/[};)]$/.test(l)) return false;
    // 行頭が記号のみ（//、#、---、===等）→ 除外
    if (/^[\/\-=*#>|]{2,}/.test(l)) return false;
    // JSONライクな行（"key": "value"）→ 除外
    if (/^\s*"[\w_-]+"\s*:/.test(l)) return false;
    // 純粋な記号行（アルファベット・かなを含まない）→ 除外
    if (!/[\w぀-鿿]/.test(l)) return false;
    return true;
  });
}

/**
 * Stage 4: TODO/未完了タスクの意味的フィルター
 * TODO・やること・課題 などのキーワードを含む行のみ抽出
 */
function extractTodoLines(lines) {
  const TODO_RE = /TODO|FIXME|やること|未完了|要対応|要確認|あとで|検討|残課題|pending/i;
  return lines.filter(l => TODO_RE.test(l));
}

/**
 * テキストから TODO を抽出する（4段階パイプライン）
 * @param {string} text
 * @returns {string[]}
 */
export function extractTodos(text) {
  const stage1 = removeCodeBlocks(text);
  const stage2 = extractCandidateLines(stage1);
  const stage3 = filterCodeLines(stage2);
  const stage4 = extractTodoLines(stage3);
  // 重複除去
  return [...new Set(stage4)];
}

// ─── Logbook（引き継ぎ記録）────────────────────────────────────────────────

/**
 * 引き継ぎエントリを記録する
 * @param {{ summary:string, todos:string[], facts:string[], decisions:string[] }} entry
 */
export async function recordHandoff(entry) {
  const stored = await chrome.storage.local.get(STORAGE_KEY_LOGBOOK);
  const log    = stored[STORAGE_KEY_LOGBOOK] || [];
  log.unshift({
    ...entry,
    ts:      Date.now(),
    version: '1.0',
  });
  if (log.length > 20) log.pop();
  await chrome.storage.local.set({ [STORAGE_KEY_LOGBOOK]: log });

  // TODO を個別に永続化
  if (entry.todos?.length) {
    await saveTodos(entry.todos);
  }
}

/**
 * 最新のログエントリを取得する
 * @param {number} limit
 * @returns {Promise<Array>}
 */
export async function getRecentHandoffs(limit = 5) {
  const stored = await chrome.storage.local.get(STORAGE_KEY_LOGBOOK);
  return (stored[STORAGE_KEY_LOGBOOK] || []).slice(0, limit);
}

/**
 * TODO を永続化する（引き継ぎ先で参照できるように）
 * @param {string[]} todos
 */
export async function saveTodos(todos) {
  await chrome.storage.local.set({ [STORAGE_KEY_TODOS]: todos });
}

/**
 * 保存済み TODO を取得する
 * @returns {Promise<string[]>}
 */
export async function loadTodos() {
  const stored = await chrome.storage.local.get(STORAGE_KEY_TODOS);
  return stored[STORAGE_KEY_TODOS] || [];
}
