'use strict';
// tool-hook.js — PostToolUse 自動フック（TODO_217）
// Claude Code のツール完了イベントを捕捉し、
// FileGuard / ChangeTracker を自動発火させる。
//
// フェーズ1（今回）: 手動呼び出し + 方式B/C 自動捕捉
// フェーズ2（TODO_217本実装）: window.claude:tool:complete 公式イベント
// 動かない完璧 < 動く不完全。フェーズ1を確実に完成させること。

import { FileGuard }    from '../core/file-guard.js';
import { ChangeTracker } from '../core/change-tracker.js';

// ─── 監視対象ツール定義 ────────────────────────────────────────────────────────

const WATCHED_TOOLS = {
  'create_file':   async (result) => {
    if (result?.path) {
      await FileGuard.onFileCreated(result.path, {
        reason:   result.reason || 'ToolHook:create_file',
        todo_ref: result.todo_ref || '',
      });
    }
  },
  'present_files': async (result) => {
    if (result?.paths?.length) {
      await FileGuard.onFilePresented(result.paths, {
        reason: 'ToolHook:present_files',
      });
    }
  },
  'str_replace':   async (result) => {
    if (result?.path) {
      await ChangeTracker.afterChange(result.path, 'success', {
        diff_summary: result.diff_summary || 'str_replace via ToolHook',
      });
    }
  },
  'Write':         async (result) => {
    if (result?.path) {
      await FileGuard.onFileCreated(result.path, {
        reason: 'ToolHook:Write',
      });
    }
  },
  'Edit':          async (result) => {
    if (result?.path) {
      await ChangeTracker.afterChange(result.path, 'success', {
        diff_summary: result.diff_summary || 'Edit via ToolHook',
      });
    }
  },
};

// ─── フック発火履歴 ────────────────────────────────────────────────────────────

const _hookLog = [];

function _logHook(tool, method, result) {
  _hookLog.push({
    tool,
    method,
    timestamp: new Date().toISOString(),
    result_summary: result ? JSON.stringify(result).slice(0, 120) : null,
  });
  if (_hookLog.length > 100) _hookLog.shift();
}

async function _dispatch(toolName, result, method) {
  const handler = WATCHED_TOOLS[toolName];
  if (!handler) return;

  try {
    await handler(result);
    _logHook(toolName, method, result);
    console.log(`[ToolHook] ${method} → ${toolName} 処理完了`);
  } catch (err) {
    console.warn(`[ToolHook] ${toolName} ハンドラエラー:`, err.message);
  }
}

// ─── 方式B: chrome.runtime.onMessage ──────────────────────────────────────────

function _onChromeMessage(msg) {
  if (msg?.type === 'CLAUDE_TOOL_COMPLETE' && msg.tool) {
    _dispatch(msg.tool, msg.result || {}, '方式B:chrome.runtime');
  }
}

// ─── 方式A: window カスタムイベント ────────────────────────────────────────────

function _onWindowEvent(event) {
  const { tool, result } = event.detail || {};
  if (tool) {
    _dispatch(tool, result || {}, '方式A:window.event');
  }
}

// ─── 方式C: MutationObserver（フォールバック）──────────────────────────────────
// Claude Code の UI に tool 名が含まれる要素を監視する。
// 精度は低いが、方式A/Bが使えない環境のためのフォールバック。

let _mutObserver = null;

function _startMutationObserver() {
  if (typeof document === 'undefined') return;

  _mutObserver = new MutationObserver((mutations) => {
    for (const m of mutations) {
      for (const node of m.addedNodes) {
        if (node.nodeType !== 1) continue;
        const text = node.textContent || '';

        // Claude Code が出力するツール完了メッセージを検出
        const match = text.match(/\[Tool\s+(create_file|present_files|str_replace|Write|Edit)\s+completed\]/i);
        if (match) {
          // パス情報は取れないため概略のみ記録
          _logHook(match[1], '方式C:MutationObserver', null);
          console.log('[ToolHook] 方式C 検出:', match[1]);
        }
      }
    }
  });

  _mutObserver.observe(document.body, { childList: true, subtree: true });
}

// ─── 公開インターフェース ──────────────────────────────────────────────────────

let _registered = false;

export const ToolHook = {
  /**
   * フック登録（初期化時に1回呼ぶ）。
   * 方式A → B → C の順で利用可能な方式を登録する。
   */
  register() {
    if (_registered) return;
    _registered = true;

    // 方式A: window カスタムイベント
    if (typeof window !== 'undefined') {
      window.addEventListener('claude:tool:complete', _onWindowEvent);
      console.log('[ToolHook] 方式A 登録: claude:tool:complete');
    }

    // 方式B: chrome.runtime.onMessage
    if (typeof globalThis.chrome !== 'undefined' && chrome.runtime?.onMessage) {
      chrome.runtime.onMessage.addListener(_onChromeMessage);
      console.log('[ToolHook] 方式B 登録: chrome.runtime.onMessage');
    }

    // 方式C: MutationObserver（フォールバック）
    if (typeof document !== 'undefined' && document.body) {
      _startMutationObserver();
      console.log('[ToolHook] 方式C 登録: MutationObserver');
    }

    console.log('[ToolHook] フック登録完了（フェーズ1）');
  },

  /**
   * フック解除。
   */
  unregister() {
    if (!_registered) return;
    _registered = false;

    if (typeof window !== 'undefined') {
      window.removeEventListener('claude:tool:complete', _onWindowEvent);
    }
    if (typeof globalThis.chrome !== 'undefined' && chrome.runtime?.onMessage) {
      chrome.runtime.onMessage.removeListener(_onChromeMessage);
    }
    if (_mutObserver) {
      _mutObserver.disconnect();
      _mutObserver = null;
    }

    console.log('[ToolHook] フック解除完了');
  },

  /**
   * フック発火履歴を返す。
   * @returns {Array}
   */
  getHookLog() {
    return [..._hookLog];
  },

  /**
   * フェーズ1: 手動でツール完了を通知する。
   * create_file / Edit などの直後に Claude Code から呼ぶ。
   * @param {string} toolName
   * @param {object} result — { path?, paths?, diff_summary?, reason? }
   */
  async notify(toolName, result = {}) {
    await _dispatch(toolName, result, '手動:notify');
  },
};
