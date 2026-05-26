// background.js
'use strict';

import { SCHEMA_VERSION, PLAN_LIMITS } from './shared/constants.js';
import { validateRegistry } from './shared/validators.js';

// ============================================================
// 初期化
// ============================================================
chrome.runtime.onInstalled.addListener(async () => {
  const existing = await chrome.storage.local.get('memory_registry');
  if (!existing.memory_registry) {
    await initRegistry();
  }
  setupContextMenus();
  setupAlarms();
});

async function initRegistry() {
  const registry = {
    schema_version: SCHEMA_VERSION,
    workspace_id: 'default',
    updated_at: new Date().toISOString(),
    plan: 'free',
    current_state: {
      last_session_id: null,
      stage: '',
      active_project: '',
      last_active: new Date().toISOString()
    },
    files: [],
    known_errors: [],
    environment: [],
    pending_todos: [],
    decisions: [],
    sessions: []
  };

  await chrome.storage.local.set({ memory_registry: registry });
}

// ============================================================
// メッセージハンドラ
// ============================================================
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  (async () => {
    switch (msg.type) {

      case 'MEMORY_CAPTURE':
        await handleCapture(msg.payload);
        sendResponse({ ok: true });
        break;

      case 'MEMORY_GET_REGISTRY':
        const reg = await getRegistry();
        sendResponse({ registry: reg });
        break;

      case 'MEMORY_GET_INJECT_BLOCK':
        const block = await buildInjectBlock();
        sendResponse({ block });
        break;

      case 'MEMORY_ADD_MANUAL':
        await addManualEntry(msg.payload);
        sendResponse({ ok: true });
        break;

      case 'MEMORY_CLEAR_SESSION':
        await clearCurrentSession();
        sendResponse({ ok: true });
        break;

      case 'MEMORY_ERROR_INTERCEPT':
        const warning = await checkErrorIntercept(msg.payload.text);
        sendResponse({ warning });
        break;

      case 'MEMORY_TIME_MACHINE':
        const result = await timeMachineSearch(msg.payload.filename);
        sendResponse({ result });
        break;
    }
  })();
  return true;
});

// ============================================================
// キャプチャ処理
// ============================================================
async function handleCapture(payload) {
  const registry = await getRegistry();
  let changed = false;

  for (const fileInfo of payload.paths) {
    const exists = registry.files.find(f => f.path === fileInfo.path);
    if (!exists) {
      const newFile = {
        id: `file_${Date.now()}`,
        path: fileInfo.path,
        filename: fileInfo.path.split(/[\\\/]/).pop(),
        ext: '.' + fileInfo.path.split('.').pop(),
        status: 'stable',
        hash: '',
        summary: '',
        captured_at: payload.timestamp,
        source: 'auto'
      };

      const plan = registry.plan || 'free';
      if (plan === 'free' && registry.files.length >= PLAN_LIMITS.free.max_files) {
        registry.files.shift();
      }

      registry.files.push(newFile);
      changed = true;
    }
  }

  for (const errorInfo of payload.errors) {
    const exists = registry.known_errors.find(
      e => e.error_pattern.toLowerCase().includes(errorInfo.keyword.toLowerCase())
    );
    if (exists) {
      exists.occurrence_count++;
      exists.last_seen = payload.timestamp.split('T')[0];
    } else {
      if (registry.plan === 'free' && registry.known_errors.length >= PLAN_LIMITS.free.max_errors) {
        registry.known_errors.shift();
      }
      registry.known_errors.push({
        id: `err_${Date.now()}`,
        signature_hash: `err_auto_${Date.now()}`,
        error_pattern: errorInfo.keyword,
        trigger_keywords: [errorInfo.keyword],
        solution: '',
        occurrence_count: 1,
        last_seen: payload.timestamp.split('T')[0],
        resolved: false,
        severity: 'warning'
      });
      changed = true;
    }
  }

  if (registry.plan !== 'free') {
    for (const dec of payload.decisions) {
      registry.decisions.push({
        id: `dec_${Date.now()}`,
        content: dec.content,
        decided_at: payload.timestamp.split('T')[0],
        session_id: registry.current_state.last_session_id
      });
      if (registry.decisions.length > 50) registry.decisions.shift();
      changed = true;
    }
  }

  if (changed) {
    registry.updated_at = new Date().toISOString();
    await saveRegistry(registry);
  }
}

// ============================================================
// 注入ブロック生成
// ============================================================
async function buildInjectBlock() {
  const registry = await getRegistry();
  const lines = ['[MEMORY]'];

  const recentFiles = registry.files.slice(-5);
  if (recentFiles.length > 0) {
    lines.push('最終作業ファイル:');
    for (const f of recentFiles) {
      lines.push(`  - ${f.filename} (${f.status}) → ${f.path}`);
      if (f.summary) lines.push(`    要約: ${f.summary}`);
    }
  }

  const unresolved = registry.known_errors.filter(e => !e.resolved);
  if (unresolved.length > 0) {
    lines.push('既知エラー（未解決）:');
    for (const e of unresolved) {
      lines.push(`  ⚠️ ${e.error_pattern} (${e.occurrence_count}回発生)`);
      if (e.solution) lines.push(`  → 対策: ${e.solution}`);
    }
  }

  if (registry.environment.length > 0) {
    lines.push('環境制約:');
    for (const env of registry.environment) {
      lines.push(`  • ${env}`);
    }
  }

  if (registry.pending_todos.length > 0) {
    lines.push('未完了TODO:');
    for (const todo of registry.pending_todos.slice(0, 3)) {
      lines.push(`  [ ] ${todo.id}: ${todo.title}`);
    }
  }

  if (registry.plan !== 'free' && registry.decisions.length > 0) {
    lines.push('直近の決定事項:');
    for (const dec of registry.decisions.slice(-3)) {
      lines.push(`  ✓ ${dec.decided_at}: ${dec.content}`);
    }
  }

  return lines.join('\n');
}

// ============================================================
// エラーインターセプト
// ============================================================
async function checkErrorIntercept(text) {
  const registry = await getRegistry();
  const lowerText = text.toLowerCase();

  for (const err of registry.known_errors) {
    for (const keyword of err.trigger_keywords) {
      if (lowerText.includes(keyword.toLowerCase())) {
        return {
          triggered: true,
          severity: err.severity,
          message: `⚠️ 過去${err.occurrence_count}回発生: ${err.error_pattern}`,
          solution: err.solution
        };
      }
    }
  }
  return { triggered: false };
}

// ============================================================
// Time Machine（Oneプラン）
// ============================================================
async function timeMachineSearch(filename) {
  const registry = await getRegistry();
  if (registry.plan !== 'one') return { error: 'One plan required' };

  const fileRecord = registry.files.find(f => f.filename === filename);
  if (!fileRecord) return { error: 'File not found' };

  const stableSession = registry.sessions
    .filter(s => s.files_touched.includes(filename))
    .reverse()
    .find(s => {
      const idx = registry.sessions.indexOf(s);
      const later = registry.sessions.slice(idx + 1);
      return !later.some(ls => ls.errors_encountered.length > 0);
    });

  return {
    file: fileRecord,
    last_stable_session: stableSession || null,
    message: stableSession
      ? `${filename}が最後にstableだったセッション: ${stableSession.session_id}`
      : `${filename}の安定セッションが見つかりません`
  };
}

// ============================================================
// ユーティリティ
// ============================================================
async function getRegistry() {
  const data = await chrome.storage.local.get('memory_registry');
  return data.memory_registry || {};
}

async function saveRegistry(registry) {
  await chrome.storage.local.set({ memory_registry: registry });
}

async function clearCurrentSession() {
  const registry = await getRegistry();
  registry.files = registry.files.filter(f => f.source !== 'auto');
  registry.current_state.stage = '';
  await saveRegistry(registry);
}

// ============================================================
// コンテキストメニュー
// ============================================================
function setupContextMenus() {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({
      id: 'memory_copy_inject',
      title: '📋 Memoryブロックをコピー',
      contexts: ['all']
    });
    chrome.contextMenus.create({
      id: 'memory_add_env',
      title: '⚙️ 環境制約として記録',
      contexts: ['selection']
    });
    chrome.contextMenus.create({
      id: 'memory_add_error',
      title: '🔴 エラー解決策として記録',
      contexts: ['selection']
    });
    chrome.contextMenus.create({
      id: 'memory_mark_decision',
      title: '✅ 決定事項として記録',
      contexts: ['selection']
    });
  });
}

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  const registry = await getRegistry();

  switch (info.menuItemId) {
    case 'memory_copy_inject':
      const block = await buildInjectBlock();
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (text) => navigator.clipboard.writeText(text),
        args: [block]
      });
      break;

    case 'memory_add_env':
      if (info.selectionText) {
        registry.environment.push(info.selectionText.trim());
        await saveRegistry(registry);
      }
      break;

    case 'memory_add_error':
      if (info.selectionText) {
        registry.known_errors.push({
          id: `err_${Date.now()}`,
          signature_hash: `err_manual_${Date.now()}`,
          error_pattern: info.selectionText.trim().substring(0, 100),
          trigger_keywords: [],
          solution: '',
          occurrence_count: 1,
          last_seen: new Date().toISOString().split('T')[0],
          resolved: false,
          severity: 'warning'
        });
        await saveRegistry(registry);
      }
      break;

    case 'memory_mark_decision':
      if (info.selectionText && registry.plan !== 'free') {
        registry.decisions.push({
          id: `dec_${Date.now()}`,
          content: info.selectionText.trim().substring(0, 200),
          decided_at: new Date().toISOString().split('T')[0],
          session_id: registry.current_state.last_session_id
        });
        await saveRegistry(registry);
      }
      break;
  }
});

// ============================================================
// 定期クリーンアップ
// ============================================================
function setupAlarms() {
  chrome.alarms.create('memory_cleanup', { periodInMinutes: 60 });
}

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === 'memory_cleanup') {
    const registry = await getRegistry();
    if (registry.plan === 'free') {
      if (registry.files.length > 20) {
        registry.files = registry.files.slice(-20);
        await saveRegistry(registry);
      }
    }
  }
});
