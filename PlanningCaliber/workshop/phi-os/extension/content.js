// PHI OS content.js v2.0 - Inline Bundle (content script compatible)
// chrome拡張のcontent_scriptsはES module importが使えないため完全インライン展開
// claude.ai に注入される唯一のスクリプト
// IndexedDB / DOM操作はここで行う
'use strict';

// ============================================================
// [INLINE] core/i18n.js
// ============================================================
const PHI_I18N = {
  ja: {
    restore_complete: 'PHI OS: コンテキスト復元完了',
    restore_title: '🧠 前回の記憶を復元しました',
    restore_btn_ok: '確認',
    restore_btn_skip: 'スキップ',
    commit_title: '📦 セッションを保存しますか？',
    commit_btn_yes: '保存する',
    commit_btn_no: '後で',
    session_saved: 'セッション保存完了',
    debug_title: 'PHI OS Debug',
  },
  en: {
    restore_complete: 'PHI OS: Context restored',
    restore_title: '🧠 Previous session restored',
    restore_btn_ok: 'OK',
    restore_btn_skip: 'Skip',
    commit_title: '📦 Save this session?',
    commit_btn_yes: 'Save',
    commit_btn_no: 'Later',
    session_saved: 'Session saved',
    debug_title: 'PHI OS Debug',
  },
  zh: {
    restore_complete: 'PHI OS: 上下文已恢复',
    restore_title: '🧠 已恢复上次会话',
    restore_btn_ok: '确认',
    restore_btn_skip: '跳过',
    commit_title: '📦 保存本次会话？',
    commit_btn_yes: '保存',
    commit_btn_no: '稍后',
    session_saved: '会话已保存',
    debug_title: 'PHI OS 调试',
  },
  ko: {
    restore_complete: 'PHI OS: 컨텍스트 복원 완료',
    restore_title: '🧠 이전 세션이 복원되었습니다',
    restore_btn_ok: '확인',
    restore_btn_skip: '건너뛰기',
    commit_title: '📦 이 세션을 저장할까요?',
    commit_btn_yes: '저장',
    commit_btn_no: '나중에',
    session_saved: '세션 저장 완료',
    debug_title: 'PHI OS 디버그',
  },
  de: {
    restore_complete: 'PHI OS: Kontext wiederhergestellt',
    restore_title: '🧠 Vorherige Sitzung wiederhergestellt',
    restore_btn_ok: 'OK',
    restore_btn_skip: 'Überspringen',
    commit_title: '📦 Diese Sitzung speichern?',
    commit_btn_yes: 'Speichern',
    commit_btn_no: 'Später',
    session_saved: 'Sitzung gespeichert',
    debug_title: 'PHI OS Debug',
  },
};

function initI18n() {
  const lang = navigator.language ? navigator.language.split('-')[0] : 'en';
  return PHI_I18N[lang] || PHI_I18N['en'];
}

// ============================================================
// [INLINE] core/schema-registry.js
// ============================================================
const PHI_SCHEMA_VERSION = 2;
const PHI_DB_NAME = 'phi_os_db';
const PHI_STORE_SESSIONS = 'sessions';
const PHI_STORE_RESTORE = 'restore_packets';
const PHI_STORE_META = 'meta';

function ensureSchemaVersion(db) {
  // called during onupgradeneeded - handled in openDb
  return true;
}

// ============================================================
// [INLINE] core/restore-engine.js
// ============================================================
function buildRestorePacket(sessions) {
  if (!sessions || sessions.length === 0) return null;
  const latest = sessions[0];
  const decisions = [];
  const files = [];
  const todos = [];

  sessions.slice(0, 5).forEach(s => {
    if (s.decisions) decisions.push(...s.decisions);
    if (s.files) files.push(...s.files);
    if (s.todos) todos.push(...s.todos);
  });

  return {
    version: PHI_SCHEMA_VERSION,
    generated_at: new Date().toISOString(),
    last_session_id: latest.session_id,
    decisions: decisions.slice(0, 10),
    files: [...new Set(files)].slice(0, 20),
    todos: todos.filter(t => t.status !== 'done').slice(0, 10),
    summary: latest.summary || '',
    tensions: latest.tensions || [],
  };
}

// ============================================================
// [INLINE] core/auto-trigger.js
// ============================================================
const AUTO_TRIGGER_INTERVAL_MS = 300000; // 5分

class AutoTrigger {
  constructor(onTrigger) {
    this._cb = onTrigger;
    this._timer = null;
  }
  start() {
    this._timer = setInterval(() => this._cb(), AUTO_TRIGGER_INTERVAL_MS);
  }
  stop() {
    if (this._timer) clearInterval(this._timer);
  }
}

// ============================================================
// [INLINE] debug/error-reporter.js
// ============================================================
function installGlobalHandlers() {
  window.addEventListener('error', (e) => {
    console.error('[PHI OS] Uncaught error:', e.message, e.filename, e.lineno);
  });
  window.addEventListener('unhandledrejection', (e) => {
    console.error('[PHI OS] Unhandled rejection:', e.reason);
  });
}

// ============================================================
// [INLINE] debug/debug-panel.js
// ============================================================

// ─── Drag Support ─────────────────────────────────────────────────────────────
function makeDraggable(el, storageKey, defaultRight, defaultBottom) {
  if (typeof chrome === 'undefined' || !chrome.storage) return;
  chrome.storage.local.get(storageKey, (r) => {
    const pos = r[storageKey];
    if (pos) {
      el.style.left = pos.left + 'px'; el.style.top = pos.top + 'px';
      el.style.right = 'auto'; el.style.bottom = 'auto';
    }
  });
  let isDragging = false, startX, startY, startLeft, startTop;
  el.addEventListener('mousedown', (e) => {
    if (e.button !== 0) return;
    isDragging = false;
    const rect = el.getBoundingClientRect();
    startX = e.clientX; startY = e.clientY;
    startLeft = rect.left; startTop = rect.top;
    el.style.left = startLeft + 'px'; el.style.top = startTop + 'px';
    el.style.right = 'auto'; el.style.bottom = 'auto';
    const onMove = (e) => {
      const dx = e.clientX - startX, dy = e.clientY - startY;
      if (Math.abs(dx) > 5 || Math.abs(dy) > 5) isDragging = true;
      if (isDragging) {
        el.style.left = Math.max(0, Math.min(window.innerWidth  - el.offsetWidth,  startLeft + dx)) + 'px';
        el.style.top  = Math.max(0, Math.min(window.innerHeight - el.offsetHeight, startTop  + dy)) + 'px';
      }
    };
    const onUp = () => {
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
      if (isDragging) chrome.storage.local.set({ [storageKey]: { left: parseInt(el.style.left), top: parseInt(el.style.top) } });
    };
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
    e.preventDefault();
  });
  el.addEventListener('click', (e) => { if (isDragging) { e.stopImmediatePropagation(); isDragging = false; } }, true);
  el.style.cursor = 'grab';
}

class DebugPanel {
  constructor(i18n) {
    this._i18n = i18n;
    this._el = null;
    this._visible = false;
  }

  toggle() {
    if (this._visible) {
      this.hide();
    } else {
      this.show();
    }
  }

  show() {
    if (!this._el) this._el = this._create();
    this._el.style.display = 'block';
    this._visible = true;
    this._update();
  }

  hide() {
    if (this._el) this._el.style.display = 'none';
    this._visible = false;
  }

  _create() {
    const el = document.createElement('div');
    el.id = 'phi-os-debug';
    el.style.cssText = [
      'position:fixed', 'bottom:30px', 'right:16px', 'z-index:8800',
      'background:#1a1a2e', 'color:#e2e8f0', 'border:1px solid #4a5568',
      'border-radius:8px', 'padding:12px 16px', 'font-family:monospace',
      'font-size:12px', 'max-width:320px', 'box-shadow:0 4px 24px rgba(0,0,0,0.5)',
    ].join(';');
    el.innerHTML = `<div style="font-weight:bold;margin-bottom:8px;color:#90cdf4">${this._i18n.debug_title}</div><div id="phi-debug-body"></div>`;
    document.body.appendChild(el);
    makeDraggable(el, 'phios_badge_pos', 16, 30);
    return el;
  }

  _update() {
    if (!this._el) return;
    const body = this._el.querySelector('#phi-debug-body');
    if (!body) return;
    body.innerHTML = [
      `version: ${PHI_SCHEMA_VERSION}`,
      `url: ${location.pathname.substring(0, 30)}`,
      `lang: ${navigator.language}`,
      `time: ${new Date().toLocaleTimeString()}`,
    ].map(l => `<div>${l}</div>`).join('');
  }
}

// ============================================================
// メイン: PHI OS コアロジック
// ============================================================

let _db = null;
let _i18n = null;
let _debugPanel = null;
let _autoTrigger = null;
let _restoreShown = false;

/** IndexedDB を開く */
function openDb() {
  return new Promise((resolve, reject) => {
    if (_db) { resolve(_db); return; }
    const req = indexedDB.open(PHI_DB_NAME, PHI_SCHEMA_VERSION);
    req.onupgradeneeded = (e) => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains(PHI_STORE_SESSIONS)) {
        const s = db.createObjectStore(PHI_STORE_SESSIONS, { keyPath: 'session_id' });
        s.createIndex('by_created', 'created_at');
      }
      if (!db.objectStoreNames.contains(PHI_STORE_RESTORE)) {
        db.createObjectStore(PHI_STORE_RESTORE, { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains(PHI_STORE_META)) {
        db.createObjectStore(PHI_STORE_META, { keyPath: 'key' });
      }
    };
    req.onsuccess = (e) => { _db = e.target.result; resolve(_db); };
    req.onerror = (e) => reject(e.target.error);
  });
}

/** 最新セッションを取得 */
function getRecentSessions(limit = 5) {
  return openDb().then(db => new Promise((resolve, reject) => {
    const tx = db.transaction(PHI_STORE_SESSIONS, 'readonly');
    const store = tx.objectStore(PHI_STORE_SESSIONS);
    const idx = store.index('by_created');
    const req = idx.openCursor(null, 'prev');
    const results = [];
    req.onsuccess = (e) => {
      const cursor = e.target.result;
      if (cursor && results.length < limit) {
        results.push(cursor.value);
        cursor.continue();
      } else {
        resolve(results);
      }
    };
    req.onerror = (e) => reject(e.target.error);
  }));
}

/** セッション保存 */
function saveSession(data) {
  return openDb().then(db => new Promise((resolve, reject) => {
    const tx = db.transaction(PHI_STORE_SESSIONS, 'readwrite');
    const store = tx.objectStore(PHI_STORE_SESSIONS);
    const record = Object.assign({
      session_id: 'sess_' + Date.now(),
      created_at: new Date().toISOString(),
      url: location.href,
    }, data);
    const req = store.put(record);
    req.onsuccess = () => resolve(record);
    req.onerror = (e) => reject(e.target.error);
  }));
}

/** Restore Packet を表示 */
function showRestoreUI(packet) {
  if (_restoreShown) return;
  _restoreShown = true;

  const overlay = document.createElement('div');
  overlay.id = 'phi-os-restore-overlay';
  overlay.style.cssText = [
    'position:fixed', 'top:16px', 'right:16px', 'z-index:2147483646',
    'background:#1a1a2e', 'color:#e2e8f0', 'border:1px solid #4299e1',
    'border-radius:12px', 'padding:16px 20px', 'max-width:380px',
    'box-shadow:0 8px 32px rgba(0,0,0,0.6)', 'font-family:sans-serif',
    'font-size:13px', 'animation:phi-fadein 0.3s ease',
  ].join(';');

  const style = document.createElement('style');
  style.textContent = '@keyframes phi-fadein{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:translateY(0)}}';
  document.head.appendChild(style);

  const lines = [];
  if (packet.decisions && packet.decisions.length > 0) {
    lines.push(`<div style="margin-top:8px;color:#90cdf4">📋 直近の決定: ${packet.decisions.length}件</div>`);
  }
  if (packet.files && packet.files.length > 0) {
    lines.push(`<div style="color:#68d391">📁 ファイル: ${packet.files.length}件</div>`);
  }
  if (packet.todos && packet.todos.length > 0) {
    lines.push(`<div style="color:#fbd38d">✅ TODO: ${packet.todos.length}件</div>`);
  }
  if (packet.tensions && packet.tensions.length > 0) {
    lines.push(`<div style="color:#fc8181">⚡ 違和感: ${packet.tensions.length}件</div>`);
  }

  overlay.innerHTML = `
    <div style="font-weight:bold;font-size:14px;margin-bottom:8px">${_i18n.restore_title}</div>
    <div style="color:#a0aec0;font-size:11px">前回: ${new Date(packet.generated_at).toLocaleString()}</div>
    ${lines.join('')}
    <div style="margin-top:12px;display:flex;gap:8px">
      <button id="phi-restore-ok" style="flex:1;padding:6px;background:#3182ce;color:white;border:none;border-radius:6px;cursor:pointer;font-size:12px">${_i18n.restore_btn_ok}</button>
      <button id="phi-restore-skip" style="flex:1;padding:6px;background:#2d3748;color:#a0aec0;border:none;border-radius:6px;cursor:pointer;font-size:12px">${_i18n.restore_btn_skip}</button>
    </div>
  `;

  document.body.appendChild(overlay);

  document.getElementById('phi-restore-ok').onclick = () => {
    injectRestorePacket(packet);
    overlay.remove();
  };
  document.getElementById('phi-restore-skip').onclick = () => {
    overlay.remove();
  };

  // 30秒後に自動的に閉じる
  setTimeout(() => { if (overlay.parentNode) overlay.remove(); }, 30000);
}

/** テキストエリアにRestore Packetを注入 */
function injectRestorePacket(packet) {
  const inputEl = document.querySelector(
    '[data-testid="composer-input"], .ProseMirror, [contenteditable="true"]'
  );
  if (!inputEl) return;

  const lines = ['[PHI OS Restore Packet]'];
  if (packet.summary) lines.push('前回のサマリー: ' + packet.summary);
  if (packet.decisions && packet.decisions.length > 0) {
    lines.push('直近の決定事項:');
    packet.decisions.slice(0, 5).forEach(d => lines.push('  - ' + d));
  }
  if (packet.files && packet.files.length > 0) {
    lines.push('関連ファイル:');
    packet.files.slice(0, 10).forEach(f => lines.push('  - ' + f));
  }
  if (packet.todos && packet.todos.length > 0) {
    lines.push('未完了TODO:');
    packet.todos.slice(0, 5).forEach(t => lines.push('  - ' + (t.title || t)));
  }
  if (packet.tensions && packet.tensions.length > 0) {
    lines.push('違和感・未解決:');
    packet.tensions.slice(0, 3).forEach(t => lines.push('  - ' + t));
  }
  lines.push('[/PHI OS Restore Packet]');

  const text = lines.join('\n');

  // ProseMirror / contenteditable
  if (inputEl.isContentEditable) {
    inputEl.focus();
    document.execCommand('insertText', false, text);
    return;
  }

  // textarea
  if (inputEl.tagName === 'TEXTAREA') {
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
    nativeInputValueSetter.call(inputEl, text);
    inputEl.dispatchEvent(new Event('input', { bubbles: true }));
  }
}

/** 新規チャット検出時にRestore Packetを確認・表示 */
async function onNewChat() {
  try {
    const sessions = await getRecentSessions(5);
    if (sessions.length === 0) return;
    const packet = buildRestorePacket(sessions);
    if (!packet) return;
    // 1秒待ってUIが安定してから表示
    setTimeout(() => showRestoreUI(packet), 1000);
  } catch (e) {
    console.warn('[PHI OS] onNewChat error:', e);
  }
}

/** Shift+Alt+P でデバッグパネルをトグル */
function setupKeyboardShortcut() {
  document.addEventListener('keydown', (e) => {
    if (e.shiftKey && e.altKey && e.key === 'P') {
      _debugPanel.toggle();
    }
  });
}

/** メッセージリスナー (background.js から) */
function setupMessageListener() {
  chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === 'PHI_SAVE_SESSION') {
      saveSession(msg.data)
        .then(r => sendResponse({ ok: true, session_id: r.session_id }))
        .catch(e => sendResponse({ ok: false, error: e.message }));
      return true; // async
    }
    if (msg.type === 'PHI_GET_RESTORE') {
      getRecentSessions(5)
        .then(sessions => {
          const packet = buildRestorePacket(sessions);
          sendResponse({ ok: true, packet });
        })
        .catch(e => sendResponse({ ok: false, error: e.message }));
      return true;
    }
    if (msg.type === 'PHI_DEBUG_TOGGLE') {
      _debugPanel.toggle();
      sendResponse({ ok: true });
    }
  });
}

/** URL変化を監視して新規チャットを検出 */
function watchNavigation() {
  let lastPath = location.pathname;
  const check = () => {
    if (location.pathname !== lastPath) {
      lastPath = location.pathname;
      if (location.pathname === '/new' || location.pathname.startsWith('/chat')) {
        _restoreShown = false; // リセット
        if (location.pathname === '/new') {
          onNewChat();
        }
      }
    }
  };
  setInterval(check, 1000);
  // pushState / replaceState をフック
  const orig = history.pushState.bind(history);
  history.pushState = function(...args) {
    orig(...args);
    setTimeout(check, 100);
  };
}

// ============================================================
// 起動
// ============================================================
(function main() {
  try {
    installGlobalHandlers();
    _i18n = initI18n();
    _debugPanel = new DebugPanel(_i18n);

    // DBを事前に開いておく（warm-up）
    openDb().catch(e => console.warn('[PHI OS] DB open failed:', e));

    setupMessageListener();
    setupKeyboardShortcut();
    watchNavigation();

    // AutoTrigger: 5分ごとにバックグラウンドに状態をpush
    _autoTrigger = new AutoTrigger(() => {
      chrome.runtime.sendMessage({ type: 'PHI_HEARTBEAT', url: location.href });
    });
    _autoTrigger.start();

    // 現在のページが新規チャットなら即Restore確認
    if (location.pathname === '/new') {
      onNewChat();
    }

    console.log('[PHI OS] content.js v2.0 initialized (inline bundle)');
  } catch (e) {
    console.error('[PHI OS] init failed:', e);
  }
})();
