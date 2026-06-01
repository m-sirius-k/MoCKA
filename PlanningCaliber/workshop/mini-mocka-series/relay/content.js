// content.js — Relay content script（claude.ai ページ上で動作）
// Task 3: LB_005 修正済み — init() から notifySessionStart を削除
'use strict';

import { addMessage, init, getState } from './relay-main.js';
import { extractTodos, recordHandoff, loadTodos } from './relay-logbook.js';

// ─── DOM 監視 ────────────────────────────────────────────────────────────────

const TURN_SELECTOR    = '[data-testid="human-turn"], [data-testid="ai-turn"]';
const INPUT_SELECTOR   = 'div[contenteditable="true"]';

let _observer   = null;
let _seenTurnIds = new Set();

function observeTurns() {
  const target = document.querySelector('main') || document.body;
  _observer = new MutationObserver(() => _scanTurns());
  _observer.observe(target, { childList: true, subtree: true });
  _scanTurns();  // 初回スキャン
}

function _scanTurns() {
  const turns = document.querySelectorAll(TURN_SELECTOR);
  turns.forEach(turn => {
    const id = turn.getAttribute('data-turn-id') || turn.textContent?.slice(0, 30);
    if (!id || _seenTurnIds.has(id)) return;
    _seenTurnIds.add(id);
    const role    = turn.dataset.testid?.includes('human') ? 'user' : 'assistant';
    const content = turn.textContent?.trim() || '';
    addMessage(role, content);
    window.dispatchEvent(new CustomEvent('relay:turn-added', { detail: { role, content } }));
  });
}

// ─── 引き継ぎ処理 ────────────────────────────────────────────────────────────

async function handleHandoffRequest(e) {
  const { messages, turnCount } = e.detail || {};
  if (!messages?.length) return;

  const allText   = messages.map(m => m.content).join('\n');
  const todos     = extractTodos(allText);
  const decisions = _extractDecisions(allText);
  const facts     = _extractFacts(allText);
  const summary   = `${turnCount}ターン / 重要決定 ${decisions.length}件 / TODO ${todos.length}件`;

  await recordHandoff({ summary, todos, decisions, facts });

  // 引き継ぎプロンプトをクリップボードへ
  const prompt = _buildHandoffPrompt({ summary, todos, decisions, facts });
  await navigator.clipboard.writeText(prompt).catch(() => {});

  _showHandoffToast(summary);
}

function _extractDecisions(text) {
  const RE = /([^。\n]*(?:採用|却下|確定|決定|にした|にします)[^。\n]*)/g;
  return [...text.matchAll(RE)].map(m => m[1].trim()).slice(0, 10);
}

function _extractFacts(text) {
  const RE = /([A-Z]:\\[\w\\.\- ]+|\b[\w\-]+\.(?:js|py|json|ts|md)\b)/g;
  return [...new Set(text.match(RE) || [])].slice(0, 20);
}

function _buildHandoffPrompt({ summary, todos, decisions, facts }) {
  return [
    '## 引き継ぎサマリー',
    summary,
    '',
    todos.length     ? `## TODO\n${todos.map(t => `- ${t}`).join('\n')}` : '',
    decisions.length ? `## 確定事項\n${decisions.map(d => `- ${d}`).join('\n')}` : '',
    facts.length     ? `## 関連ファイル\n${facts.map(f => `- ${f}`).join('\n')}` : '',
  ].filter(Boolean).join('\n');
}

function _showHandoffToast(summary) {
  const el = document.createElement('div');
  el.style.cssText = 'position:fixed;top:20px;right:20px;z-index:99999;background:#3fb950;color:#07090f;padding:10px 16px;border-radius:8px;font-weight:700;font-size:13px;';
  el.textContent = `✅ 引き継ぎ準備完了: ${summary}`;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 4000);
}

// ─── 初期化 ──────────────────────────────────────────────────────────────────

async function init_content() {
  // プラン判定（chrome.storage から取得）
  const stored = await chrome.storage.local.get('relay_plan_level');
  const plan   = stored['relay_plan_level'] || 'free';

  // LB_005 修正: init() を呼ぶだけ。notifySessionStart はここから呼ばない。
  // notifySessionStart はセッション開始の別イベントハンドラーでのみ呼び出す。
  init(plan);

  observeTurns();

  window.addEventListener('relay:handoff-request', handleHandoffRequest);

  // セッション開始通知（init() とは分離）
  chrome.runtime.sendMessage({ type: 'SESSION_STARTED', plan }).catch(() => {});
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init_content);
} else {
  init_content();
}
