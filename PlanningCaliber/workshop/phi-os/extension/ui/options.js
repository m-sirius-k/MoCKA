// options.js — PHI OS Dashboard ロジック
'use strict';

import { initI18n, setLang, t, getLang } from '../core/i18n.js';
import { detectMode, getBytesInUse, get, set } from '../core/state-store.js';
import { CommitEngine }  from '../core/commit-engine.js';
import { RestoreEngine } from '../core/restore-engine.js';
import { togglePanelMode } from './panel-switch.js';
import { getErrorLog, clearErrorLog } from '../debug/error-reporter.js';

const MANUAL_DATA = {
  ja: {
    sections: [
      { title: 'PHI OSとは', body: 'PHI OSはClaude.aiのセッション間の記憶断絶を解決するChrome拡張です。会話が終わるたびに自動で内容を保存し、次のセッション開始時に重要な文脈を復元します。' },
      { title: '保存の仕組み', body: 'セッション中の作業は①タブを閉じる直前 ②タブを切り替えたとき ③20ターン経過 ④5分間操作なし のタイミングで自動保存されます。保存内容は「新事実・決定事項・未完了タスク・違和感・次回起動ポイント」の5種類です。' },
      { title: '復元の仕組み', body: 'claude.ai/new（新規チャット）を開いた際に、PHI OSが前回セッションの重要な内容を自動的に入力欄に差し込みます。最大3000文字分の文脈を復元します。' },
      { title: 'モード切り換え', body: 'スタンドアロンモード（デフォルト）はサーバー接続ゼロ。Connected Modeはlocalhost:5000のMoCKAサーバー起動時に自動有効化されます。' },
      { title: '言語切り換え', body: '右上の言語セレクターで日本語・English・中文・한국어・Españolに切り換えられます。' },
      {
        title: 'トラブルシューティング',
        qa: [
          { q: '復元が実行されない', a: 'claude.ai/new を開いてください。既存チャットでは復元は実行されません。' },
          { q: '保存されていないようだ', a: 'chrome://extensions でPHI OSが有効か確認してください。ストレージ満杯の場合は古いデータを削除してください。' },
          { q: 'MoCKA接続モードにならない', a: 'MoCKA-START.bat でMoCKAサーバーを起動してlocalhost:5000を応答状態にしてください。' },
        ],
      },
    ],
  },
  en: {
    sections: [
      { title: 'What is PHI OS', body: 'PHI OS is a Chrome extension that solves the memory gap between Claude.ai sessions. It automatically saves your work and restores important context when you start a new session.' },
      { title: 'How Saving Works', body: 'Your session is automatically saved when: ① closing the tab ② switching tabs ③ 20 turns have passed ④ idle for 5 minutes. Saved content: facts, decisions, TODOs, tensions, next session hook.' },
      { title: 'How Restore Works', body: 'When you open claude.ai/new, PHI OS injects key context from your last session into the input field. Up to 3,000 characters are restored.' },
      { title: 'Mode Switching', body: 'Standalone Mode (default) requires no server. Connected Mode auto-activates when MoCKA server is running at localhost:5000.' },
      { title: 'Language Switching', body: 'Use the language selector in the top right to switch between 日本語, English, 中文, 한국어, and Español.' },
      {
        title: 'Troubleshooting',
        qa: [
          { q: 'Restore is not working', a: 'Open claude.ai/new. Restore only runs on new chat pages.' },
          { q: "Content doesn't seem to be saved", a: 'Check that PHI OS is enabled at chrome://extensions. Use the Delete Old Data button if storage is full.' },
          { q: 'MoCKA Connected Mode not activating', a: 'Start the MoCKA server with MoCKA-START.bat so localhost:5000 is responsive.' },
        ],
      },
    ],
  },
};

// ─── Init ────────────────────────────────────────────────────────────────────

async function init() {
  await initI18n();
  bindEvents();
  await refreshAll();
}

// ─── Refresh ──────────────────────────────────────────────────────────────────

async function refreshAll() {
  await Promise.all([
    refreshMode(),
    refreshStorage(),
    refreshCommitList(),
    refreshSettings(),
    refreshManual(),
  ]);
}

async function refreshMode() {
  const mode = await detectMode();
  const modeEl = document.getElementById('mode-value');
  if (modeEl) {
    modeEl.textContent = mode === 'CONNECTED' ? 'CONNECTED' : 'STANDALONE';
    modeEl.style.color = mode === 'CONNECTED' ? 'var(--green)' : 'var(--accent2)';
  }

  // 製品存在確認（chrome.storage.localに登録キーがあるか）
  const products = { relay: 'relay_current', orchestra: 'phi_orchestra_session_latest', memory: 'phi_memory_entry' };
  for (const [name, key] of Object.entries(products)) {
    const dot = document.getElementById(`dot-${name}`);
    if (!dot) continue;
    try {
      const stored = await chrome.storage.local.get(key);
      const exists = key in stored;
      dot.className = `status-dot ${exists ? 'green' : 'red'}`;
    } catch {
      dot.className = 'status-dot red';
    }
  }

  const dotMocka = document.getElementById('dot-mocka');
  if (dotMocka) dotMocka.className = `status-dot ${mode === 'CONNECTED' ? 'green' : 'red'}`;
}

async function refreshStorage() {
  const bytes = await getBytesInUse();
  const MB     = 1024 * 1024;
  const used   = (bytes / MB).toFixed(2);
  const pct    = Math.min(100, bytes / (5 * MB) * 100);

  const fill = document.getElementById('storage-fill');
  const text = document.getElementById('storage-text');
  if (fill) {
    fill.style.width = `${pct}%`;
    fill.className = `storage-fill${pct > 80 ? ' danger' : pct > 60 ? ' warn' : ''}`;
  }
  if (text) text.textContent = `${used} / 5 MB`;
}

async function refreshCommitList() {
  const index = await get('phi_commit_index', []);
  const list  = document.getElementById('commit-list');
  if (!list) return;

  if (!index.length) {
    list.innerHTML = '<div class="empty">まだコミットがありません</div>';
    return;
  }

  const items = [];
  for (const id of index.slice(0, 10)) {
    const c = await get(`phi_commit_${id}`);
    if (!c) continue;
    const d  = new Date(c.ts);
    const ds = `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
    const summary = [
      c.facts?.length      ? `${c.facts.length}files`     : '',
      c.todos?.length      ? `${c.todos.length}todos`      : '',
      c.decisions?.length  ? `${c.decisions.length}dec`    : '',
    ].filter(Boolean).join(' ');

    items.push(`
      <div class="commit-item">
        <span class="commit-trigger">${c.trigger || '?'}</span>
        <span class="commit-ts">${ds}</span>
        <span class="commit-summary">${summary || '—'}</span>
      </div>
    `);
  }
  list.innerHTML = items.join('') || '<div class="empty">まだコミットがありません</div>';
}

async function refreshSettings() {
  const { phi_connected_mode, phi_restore_enabled } = await chrome.storage.local.get([
    'phi_connected_mode', 'phi_restore_enabled',
  ]);
  const toggleConn    = document.getElementById('toggle-connected');
  const toggleRestore = document.getElementById('toggle-restore');
  if (toggleConn)    toggleConn.checked    = phi_connected_mode !== false;
  if (toggleRestore) toggleRestore.checked = phi_restore_enabled !== false;
}

function refreshManual() {
  const lang = getLang();
  const data = MANUAL_DATA[lang] || MANUAL_DATA['en'];
  const el   = document.getElementById('manual-content');
  if (!el) return;

  const html = data.sections.map(sec => {
    if (sec.qa) {
      const qaHtml = sec.qa.map(({ q, a }) =>
        `<div class="manual-qa"><div class="q">Q: ${q}</div><div class="a">${a}</div></div>`
      ).join('');
      return `<div class="manual-item"><h3>${sec.title}</h3>${qaHtml}</div>`;
    }
    return `<div class="manual-item"><h3>${sec.title}</h3><p>${sec.body}</p></div>`;
  }).join('');
  el.innerHTML = html;
}

// ─── Events ───────────────────────────────────────────────────────────────────

function bindEvents() {
  // 言語切り換え
  document.getElementById('lang-select')?.addEventListener('change', async (e) => {
    await setLang(e.target.value);
    refreshManual();
  });

  // セッション保存
  document.getElementById('btn-commit')?.addEventListener('click', async () => {
    showToast(t('status_committing'));
    try {
      const engine = new CommitEngine();
      const result = await engine.commit({ trigger: 'MANUAL' });
      await refreshAll();
      showToast(result ? t('status_saved') : t('err_no_content'));
    } catch (e) {
      showToast(t('status_error'), true);
    }
  });

  // 復元
  document.getElementById('btn-restore')?.addEventListener('click', async () => {
    const engine = new RestoreEngine();
    const packet = await engine.buildPacket();
    if (!packet) { showToast(t('err_no_content')); return; }
    await navigator.clipboard.writeText(packet);
    showToast(t('status_restored') + ' (クリップボードにコピーしました)');
  });

  // エクスポート
  document.getElementById('btn-export')?.addEventListener('click', async () => {
    const index   = await get('phi_commit_index', []);
    const commits = [];
    for (const id of index) {
      const c = await get(`phi_commit_${id}`);
      if (c) commits.push(c);
    }
    const blob = new Blob([JSON.stringify(commits, null, 2)], { type: 'application/json' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = `phi-os-export-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  });

  // パネル切り換え
  document.getElementById('btn-panel')?.addEventListener('click', async () => {
    const next = await togglePanelMode();
    showToast(`Panel: ${next}`);
  });

  // Connected Mode トグル
  document.getElementById('toggle-connected')?.addEventListener('change', async (e) => {
    await chrome.storage.local.set({ phi_connected_mode: e.target.checked });
    // モードキャッシュをリセット
    const { invalidateModeCache } = await import('../core/state-store.js');
    invalidateModeCache();
    await refreshMode();
  });

  // Restore トグル
  document.getElementById('toggle-restore')?.addEventListener('change', async (e) => {
    await chrome.storage.local.set({ phi_restore_enabled: e.target.checked });
  });

  // Health Check
  document.getElementById('btn-health')?.addEventListener('click', async () => {
    const { HealthCheck } = await import('../debug/health-check.js');
    const hc      = new HealthCheck();
    const results = await hc.run();
    const pre     = document.getElementById('health-result');
    if (pre) {
      pre.textContent = results.map(r => `[${r.status}] ${r.name}: ${r.detail || 'ok'}`).join('\n');
      pre.classList.add('visible');
    }
  });

  // エラーログクリア
  document.getElementById('btn-clear-log')?.addEventListener('click', async () => {
    await clearErrorLog();
    showToast('エラーログをクリアしました');
  });

  // 言語セレクターの初期値を合わせる
  const sel = document.getElementById('lang-select');
  if (sel) sel.value = getLang();
}

// ─── Toast ────────────────────────────────────────────────────────────────────

let toastTimer = null;
function showToast(msg, isError = false) {
  const el = document.getElementById('toast');
  if (!el) return;
  el.textContent = msg;
  el.className   = `phi-toast${isError ? ' error' : ''}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.className = 'phi-toast hidden'; }, 2500);
}

// ─── Boot ────────────────────────────────────────────────────────────────────
// ===== MoCKA接続確認 =====
async function checkMoCKA() {
  const dot  = document.getElementById('mocka-dot');
  const text = document.getElementById('mocka-status-text');
  const detail = document.getElementById('mocka-detail');
  if (!dot) return;
  try {
    const res  = await fetch('http://127.0.0.1:5000/api/phi-os-status', { signal: AbortSignal.timeout(3000) });
    const data = await res.json();
    dot.style.background = '#4caf50';
    text.textContent = 'MoCKA Connected';
    text.style.color = '#4caf50';
    detail.textContent = `phi-os events: ${data.phi_os_events ?? 0} | endpoint: ${data.mocka_endpoint ?? ''}`;
  } catch (e) {
    dot.style.background = '#f44336';
    text.textContent = 'MoCKA Offline';
    text.style.color = '#f44336';
    detail.textContent = 'localhost:5000 に接続できません';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  checkMoCKA();
  const btn = document.getElementById('btn-mocka-check');
  if (btn) btn.addEventListener('click', checkMoCKA);
});

init();
