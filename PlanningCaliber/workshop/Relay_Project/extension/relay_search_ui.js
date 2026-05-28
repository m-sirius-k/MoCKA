// relay_search_ui.js
// Relay × Orchestra 検索UI — claude.aiに🔍パネルを注入
// Relay manifest.json の content_scripts に追記して使用
// "matches": ["https://claude.ai/*"] に追加すること

(function () {
  'use strict';

  if (window.__relay_search_ui_loaded) return;
  window.__relay_search_ui_loaded = true;

  console.log('[Relay Search] UI loaded');

  // ── 設定 ──────────────────────────────────────────────────────────────────
  const PANEL_ID   = 'relay-search-panel';
  const BTN_ID     = 'relay-search-btn';
  const TIMEOUT_MS = 5000; // Orchestra応答タイムアウト

  let _reqCounter = 0;
  let _pendingReqs = new Map(); // reqId → { resolve, reject, timer }

  // ── Orchestra postMessage応答受信 ────────────────────────────────────────

  window.addEventListener('message', (event) => {
    if (event.origin !== location.origin) return;
    const msg = event.data;
    if (!msg || msg.__source !== 'orchestra') return;

    const pending = _pendingReqs.get(msg.reqId);
    if (!pending) return;

    clearTimeout(pending.timer);
    _pendingReqs.delete(msg.reqId);
    pending.resolve(msg);
  });

  // ── Orchestra呼び出しユーティリティ ──────────────────────────────────────

  function callOrchestra(type, payload = {}) {
    return new Promise((resolve, reject) => {
      const reqId = 'req_' + (++_reqCounter) + '_' + Date.now();
      const timer = setTimeout(() => {
        _pendingReqs.delete(reqId);
        reject(new Error('Orchestra timeout — Orchestra拡張がインストールされているか確認してください'));
      }, TIMEOUT_MS);

      _pendingReqs.set(reqId, { resolve, reject, timer });
      window.postMessage({ __source: 'relay', type, reqId, ...payload }, '*');
    });
  }

  async function isOrchestraAvailable() {
    try {
      await callOrchestra('ORCHESTRA_PING');
      return true;
    } catch {
      return false;
    }
  }

  // ── 検索ボタン注入（Relayバッジの隣）──────────────────────────────────────

  function injectSearchButton() {
    if (document.getElementById(BTN_ID)) return;

    const btn = document.createElement('div');
    btn.id = BTN_ID;
    btn.title = 'Orchestra検索 — 過去会話を検索してClaude入力欄に挿入';
    btn.textContent = '🔍';
    btn.style.cssText = [
      'position:fixed', 'bottom:120px', 'right:24px',
      'width:40px', 'height:40px',
      'background:#0c1220', 'border:1px solid #1e3a5f',
      'border-radius:10px', 'display:flex', 'align-items:center',
      'justify-content:center', 'cursor:pointer',
      'z-index:999998', 'font-size:18px',
      'box-shadow:0 4px 16px rgba(0,0,0,0.6)',
      'transition:transform 0.2s ease, border-color 0.2s ease',
      'user-select:none',
    ].join(';');

    btn.addEventListener('mouseenter', () => {
      btn.style.transform     = 'scale(1.1)';
      btn.style.borderColor   = '#38bdf8';
    });
    btn.addEventListener('mouseleave', () => {
      btn.style.transform     = 'scale(1)';
      btn.style.borderColor   = '#1e3a5f';
    });
    btn.addEventListener('click', toggleSearchPanel);

    document.body.appendChild(btn);
  }

  // ── 検索パネルトグル ──────────────────────────────────────────────────────

  async function toggleSearchPanel() {
    const existing = document.getElementById(PANEL_ID);
    if (existing) { existing.remove(); return; }
    openSearchPanel();
  }

  async function openSearchPanel() {
    // Orchestraが使えるか確認
    const available = await isOrchestraAvailable();

    const panel = document.createElement('div');
    panel.id = PANEL_ID;
    panel.style.cssText = [
      'position:fixed', 'bottom:170px', 'right:24px',
      'width:340px', 'max-height:480px',
      'background:#0c1220', 'border:1px solid #1e3a5f',
      'border-radius:14px', 'z-index:999997',
      'font-family:ui-monospace,monospace',
      'box-shadow:0 8px 40px rgba(0,0,0,0.8)',
      'display:flex', 'flex-direction:column',
      'overflow:hidden',
    ].join(';');

    panel.innerHTML = `
      <div style="padding:12px 14px;border-bottom:1px solid #1e3a5f;display:flex;align-items:center;justify-content:space-between;">
        <span style="color:#38bdf8;font-size:13px;font-weight:700;">🔍 Orchestra 過去会話検索</span>
        <button id="relay-search-close" style="background:none;border:none;color:#64748b;font-size:16px;cursor:pointer;padding:0 4px;">✕</button>
      </div>

      ${!available ? `
        <div style="padding:16px;color:#f59e0b;font-size:12px;line-height:1.6;">
          ⚠ Orchestra拡張が検出できません。<br>
          Orchestraがインストール・有効化されているか確認してください。
        </div>
      ` : `
        <div style="padding:10px 12px;border-bottom:1px solid #1e3a5f;">
          <div style="display:flex;gap:6px;">
            <input id="relay-search-input" type="text" placeholder="キーワードで検索..."
              style="flex:1;background:#111827;border:1px solid #1e3a5f;border-radius:8px;
                     color:#e2e8f0;font-size:12px;padding:7px 10px;font-family:inherit;outline:none;"
            />
            <button id="relay-search-go"
              style="background:#0369a1;border:1px solid #38bdf8;border-radius:8px;
                     color:#38bdf8;font-size:12px;font-weight:700;padding:7px 12px;
                     cursor:pointer;font-family:inherit;white-space:nowrap;">
              検索
            </button>
          </div>
          <div style="margin-top:6px;display:flex;gap:6px;">
            <button id="relay-search-recent"
              style="background:transparent;border:1px solid #334155;border-radius:6px;
                     color:#64748b;font-size:10px;padding:4px 10px;cursor:pointer;font-family:inherit;">
              📅 最近の会話
            </button>
          </div>
        </div>
        <div id="relay-search-results"
          style="flex:1;overflow-y:auto;padding:8px;min-height:100px;max-height:300px;">
          <div style="color:#475569;font-size:11px;text-align:center;padding:20px;">
            キーワードを入力して検索してください
          </div>
        </div>
        <div id="relay-search-status" style="padding:6px 12px;font-size:10px;color:#475569;border-top:1px solid #1e3a5f;min-height:22px;"></div>
      `}
    `;

    document.body.appendChild(panel);

    // イベント設定
    document.getElementById('relay-search-close')?.addEventListener('click', () => panel.remove());

    if (available) {
      const input  = document.getElementById('relay-search-input');
      const goBtn  = document.getElementById('relay-search-go');
      const recent = document.getElementById('relay-search-recent');

      goBtn?.addEventListener('click', () => doSearch(input?.value || ''));
      input?.addEventListener('keydown', e => { if (e.key === 'Enter') doSearch(input.value); });
      recent?.addEventListener('click', loadRecentSessions);

      // 検索入力欄にフォーカス
      setTimeout(() => input?.focus(), 50);
    }
  }

  // ── 検索実行 ──────────────────────────────────────────────────────────────

  async function doSearch(query) {
    query = query.trim();
    if (!query) return;

    setStatus('検索中...');
    setResults('<div style="color:#475569;font-size:11px;text-align:center;padding:16px;">⏳ 検索中...</div>');

    try {
      const res = await callOrchestra('ORCHESTRA_SEARCH', { query, limit: 30 });
      const results = res.results || [];
      setStatus(`${results.length}件のセッションで見つかりました`);
      renderResults(results, query);
    } catch (e) {
      setStatus('エラー: ' + e.message);
      setResults(`<div style="color:#ef4444;font-size:11px;padding:12px;">${e.message}</div>`);
    }
  }

  // ── 最近のセッション読み込み ──────────────────────────────────────────────

  async function loadRecentSessions() {
    setStatus('読み込み中...');
    setResults('<div style="color:#475569;font-size:11px;text-align:center;padding:16px;">⏳ 読み込み中...</div>');

    try {
      const res = await callOrchestra('ORCHESTRA_GET_SESSIONS', { limit: 20 });
      const sessions = res.sessions || [];
      setStatus(`最近 ${sessions.length} セッション`);
      renderSessionList(sessions);
    } catch (e) {
      setStatus('エラー: ' + e.message);
      setResults(`<div style="color:#ef4444;font-size:11px;padding:12px;">${e.message}</div>`);
    }
  }

  // ── 検索結果レンダリング ──────────────────────────────────────────────────

  function renderResults(results, query) {
    if (!results.length) {
      setResults('<div style="color:#475569;font-size:11px;text-align:center;padding:20px;">該当なし</div>');
      return;
    }

    const html = results.map(sess => {
      const title   = escHtml(sess.title || '(タイトルなし)');
      const snippet = escHtml(sess.snippet || '');
      const date    = sess.date || '';
      const count   = sess.matched_count || 0;

      // クエリをハイライト（スニペット内）
      const highlighted = snippet.replace(
        new RegExp(escRegex(query), 'gi'),
        m => `<mark style="background:#1e3a5f;color:#38bdf8;border-radius:2px;">${m}</mark>`
      );

      return `
        <div class="rso-item" data-sid="${escHtml(sess.session_id)}"
          style="padding:10px;margin:4px 0;background:#111827;border:1px solid #1e3a5f;
                 border-radius:8px;cursor:pointer;transition:border-color 0.15s;"
          onmouseover="this.style.borderColor='#38bdf8'"
          onmouseout="this.style.borderColor='#1e3a5f'"
        >
          <div style="color:#e2e8f0;font-size:11px;font-weight:700;margin-bottom:4px;
                      white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"
               title="${title}">${title}</div>
          <div style="color:#94a3b8;font-size:10px;margin-bottom:6px;line-height:1.5;">
            ${highlighted}
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="color:#475569;font-size:9px;">${date} · ${sess.message_count}msgs · ${count}ヒット</span>
            <button class="rso-inject-btn"
              style="background:#0369a1;border:1px solid #38bdf8;border-radius:6px;
                     color:#38bdf8;font-size:9px;font-weight:700;padding:3px 8px;cursor:pointer;">
              ⚡ 挿入
            </button>
          </div>
        </div>
      `;
    }).join('');

    setResults(html);

    // 挿入ボタンイベント
    document.querySelectorAll('.rso-inject-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const item   = btn.closest('.rso-item');
        const sid    = item?.dataset?.sid;
        const title  = item?.querySelector('div')?.textContent || '';
        const snip   = results.find(r => r.session_id === sid)?.snippet || '';
        injectToInput(sid, title, snip, query);
      });
    });
  }

  function renderSessionList(sessions) {
    if (!sessions.length) {
      setResults('<div style="color:#475569;font-size:11px;text-align:center;padding:20px;">保存済み会話なし</div>');
      return;
    }

    const html = sessions.map(sess => {
      const title = escHtml(sess.title || '(タイトルなし)');
      const date  = sess.date || '';
      return `
        <div class="rso-item" data-sid="${escHtml(sess.session_id)}"
          style="padding:9px 10px;margin:4px 0;background:#111827;border:1px solid #1e3a5f;
                 border-radius:8px;cursor:pointer;transition:border-color 0.15s;
                 display:flex;align-items:center;justify-content:space-between;"
          onmouseover="this.style.borderColor='#38bdf8'"
          onmouseout="this.style.borderColor='#1e3a5f'"
        >
          <div>
            <div style="color:#e2e8f0;font-size:11px;font-weight:600;
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:200px;"
                 title="${title}">${title}</div>
            <div style="color:#475569;font-size:9px;margin-top:2px;">${date} · ${sess.message_count}msgs</div>
          </div>
          <button class="rso-inject-btn"
            style="background:#0369a1;border:1px solid #38bdf8;border-radius:6px;
                   color:#38bdf8;font-size:9px;font-weight:700;padding:3px 8px;cursor:pointer;flex-shrink:0;">
            ⚡ 挿入
          </button>
        </div>
      `;
    }).join('');

    setResults(html);

    document.querySelectorAll('.rso-inject-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const item  = btn.closest('.rso-item');
        const sid   = item?.dataset?.sid;
        const title = item?.querySelector('div div')?.textContent || '';
        injectToInput(sid, title, '', '');
      });
    });
  }

  // ── Claude入力欄への文脈挿入 ──────────────────────────────────────────────

  function injectToInput(sessionId, title, snippet, query) {
    const INPUT_SELECTORS = [
      'div[contenteditable="true"][data-testid="composer-input"]',
      'div[contenteditable="true"].ProseMirror',
      'div[contenteditable="true"]',
    ];

    let input = null;
    for (const sel of INPUT_SELECTORS) {
      input = document.querySelector(sel);
      if (input) break;
    }

    if (!input) {
      showToast('⚠ 入力欄が見つかりません', '#f59e0b');
      return;
    }

    // 挿入テキスト生成
    const contextText = buildContextText(sessionId, title, snippet, query);

    input.focus();
    const sel = window.getSelection();
    const rng = document.createRange();
    rng.selectNodeContents(input);
    rng.collapse(false); // 末尾にカーソル
    sel.removeAllRanges();
    sel.addRange(rng);

    const ok = document.execCommand('insertText', false, contextText);
    if (!ok) {
      input.innerText = (input.innerText || '') + contextText;
      input.dispatchEvent(new InputEvent('input', { bubbles: true }));
    }

    // パネルを閉じる
    document.getElementById(PANEL_ID)?.remove();

    showToast(`✓ 過去会話を挿入しました\n「${title.slice(0, 40)}」`, '#22c55e');
    console.log('[Relay Search] Injected context from session:', sessionId);
  }

  function buildContextText(sessionId, title, snippet, query) {
    const lines = [
      `[過去会話から参照: ${title}]`,
    ];
    if (snippet) {
      lines.push(`関連箇所: ${snippet}`);
    }
    if (query) {
      lines.push(`検索キーワード: ${query}`);
    }
    lines.push('');
    lines.push('上記の過去会話を踏まえて、');
    return lines.join('\n');
  }

  // ── UI ヘルパー ───────────────────────────────────────────────────────────

  function setResults(html) {
    const el = document.getElementById('relay-search-results');
    if (el) el.innerHTML = html;
  }

  function setStatus(text) {
    const el = document.getElementById('relay-search-status');
    if (el) el.textContent = text;
  }

  function showToast(msg, color = '#22c55e') {
    const el = document.createElement('div');
    el.style.cssText = [
      'position:fixed', 'bottom:180px', 'right:24px',
      `background:${color}22`, `border:1px solid ${color}`,
      'border-radius:10px', 'padding:9px 14px',
      'color:#e2e8f0', 'font-size:12px', 'z-index:9999999',
      'font-family:ui-monospace,monospace',
      'box-shadow:0 4px 16px rgba(0,0,0,0.5)',
      'max-width:300px', 'white-space:pre-line', 'line-height:1.5',
    ].join(';');
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 3000);
  }

  function escHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function escRegex(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  // ── ボタン注入タイミング ──────────────────────────────────────────────────

  function tryInject() {
    if (document.getElementById(BTN_ID)) return;
    if (document.body) {
      injectSearchButton();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', tryInject);
  } else {
    tryInject();
  }

  // SPAナビゲーション対応
  let _lastUrl = location.href;
  setInterval(() => {
    if (location.href !== _lastUrl) {
      _lastUrl = location.href;
      setTimeout(tryInject, 800);
      // URLが変わったらパネルを閉じる
      document.getElementById(PANEL_ID)?.remove();
    }
  }, 500);

})();
