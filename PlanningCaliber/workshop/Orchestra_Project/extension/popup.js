
let allMessages = [];
let currentRole = 'all';
let currentQuery = '';
let currentSort = 'desc';
let currentPeriod = 'all';

// ドリルダウン状態
let _drillSessionId = null; // null = グループ一覧, string = グループキー
let _drillIsDate    = false; // date grouping mode かどうか

function loadStats() {
  chrome.runtime.sendMessage({ type: 'GET_STATS' }, (res) => {
    if (res?.ok) {
      document.getElementById('stat-total').textContent = res.data.total;
      document.getElementById('stat-sessions').textContent = res.data.sessions;
    }
  });
}

function loadMessages(query = '') {
  currentQuery = query;
  _drillSessionId = null; // 検索時はトップに戻す
  const msg = query
    ? { type: 'GET_MESSAGES', query, limit: 500 }
    : { type: 'GET_MESSAGES', limit: 500 };
  chrome.runtime.sendMessage(msg, (res) => {
    if (res?.ok) {
      allMessages = res.data;
      renderMessages();
    }
  });
}

// ── フィルタ共通処理 ──────────────────────────────────────────────────────────
function applyFilters(messages) {
  const now = new Date();
  let filtered = messages.filter(m => {
    if (currentRole !== 'all' && m.role !== currentRole) return false;
    if (currentPeriod === 'all') return true;
    const d = new Date(m.timestamp);
    if (currentPeriod === 'today')  return d.toDateString() === now.toDateString();
    if (currentPeriod === 'week')   { const wa = new Date(now); wa.setDate(now.getDate()-7); return d >= wa; }
    if (currentPeriod === 'month')  { const ma = new Date(now); ma.setMonth(now.getMonth()-1); return d >= ma; }
    return true;
  });
  return filtered.slice().sort((a, b) =>
    currentSort === 'desc'
      ? b.timestamp.localeCompare(a.timestamp)
      : a.timestamp.localeCompare(b.timestamp)
  );
}

// ── セッションマップ構築 ──────────────────────────────────────────────────────
// session_idが1種類以下（全て同一 or 全て未設定）の場合は日付でグループ化する
function buildSessionMap(messages) {
  const uniqueSids = new Set(
    messages.map(m => m.session_id).filter(s => s && s !== 'unknown')
  );
  const useDate = uniqueSids.size <= 1; // date fallback

  const map = new Map();
  messages.forEach(m => {
    const key = useDate
      ? (m.timestamp || '').slice(0, 10) || 'unknown'
      : (m.session_id || (m.timestamp || '').slice(0, 10) || 'unknown');

    if (!map.has(key)) map.set(key, { messages: [], title: '', date: '', latestTs: '' });
    const s = map.get(key);
    s.messages.push(m);
    if (!s.title && m.role === 'user') s.title = m.content.slice(0, 30).replace(/\n/g, ' ');
    if (!s.date && m.timestamp)        s.date = m.timestamp.slice(0, 10);
    if (!m.timestamp || m.timestamp > s.latestTs) s.latestTs = m.timestamp || '';
  });

  return { map, useDate };
}

// ── メインレンダリング分岐 ────────────────────────────────────────────────────
function renderMessages() {
  const filtered = applyFilters(allMessages);
  document.getElementById('stat-showing').textContent = filtered.length;

  if (_drillSessionId) {
    // date grouping / session grouping どちらかでフィルタ
    const sessionMsgs = _drillIsDate
      ? filtered.filter(m => (m.timestamp || '').slice(0, 10) === _drillSessionId)
      : filtered.filter(m => m.session_id === _drillSessionId);
    renderSessionDetail(sessionMsgs);
  } else {
    renderGroupedSessions(filtered);
  }
}

// ── グループ一覧ビュー ────────────────────────────────────────────────────────
function renderGroupedSessions(messages) {
  const list = document.getElementById('message-list');

  if (messages.length === 0) {
    const emptyMsg = currentQuery
      ? 'No results for "' + escHtml(currentQuery) + '"'
      : 'No messages captured yet.<br>Open claude.ai and start chatting!';
    list.innerHTML = '<div class="empty-state"><div class="empty-icon">◈</div><div class="empty-text">' + emptyMsg + '</div></div>';
    return;
  }

  const { map, useDate } = buildSessionMap(messages);

  // セッションを最新順にソート
  const sessions = Array.from(map.entries()).sort((a, b) =>
    b[1].latestTs.localeCompare(a[1].latestTs)
  );

  const highlighted = (text) => currentQuery
    ? escHtml(text).replace(new RegExp(escRegex(currentQuery), 'gi'), s => '<span class="highlight">' + s + '</span>')
    : escHtml(text);

  list.innerHTML = sessions.map(([sid, data]) => {
    const title   = data.title || '(no title)';
    const count   = data.messages.length;
    const date    = data.date;
    const preview = data.messages.find(m => m.role === 'user')?.content.slice(0, 80) || '';
    return '<div class="sess-item" data-sid="' + escHtml(sid) + '">' +
      '<div class="sess-header">' +
        '<span class="sess-title">' + highlighted(title) + '</span>' +
        '<span class="sess-badge">' + count + '</span>' +
      '</div>' +
      '<div class="sess-meta">' + escHtml(date) + '</div>' +
      '<div class="sess-preview">' + highlighted(preview) + (preview.length === 80 ? '…' : '') + '</div>' +
      '<div class="sess-actions">' +
        '<span class="sess-drill">詳細 ›</span>' +
        '<button class="sess-insert-btn" data-sid="' + escHtml(sid) + '">⚡ 挿入</button>' +
      '</div>' +
    '</div>';
  }).join('');

  // ドリルダウン（date/session どちらのグループキーかをフラグに保存）
  list.querySelectorAll('.sess-item').forEach(el => {
    el.addEventListener('click', (e) => {
      if (e.target.classList.contains('sess-insert-btn')) return;
      _drillSessionId = el.dataset.sid;
      _drillIsDate    = useDate;
      renderMessages();
    });
  });

  // 挿入ボタン
  list.querySelectorAll('.sess-insert-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const sid  = btn.dataset.sid;
      const data = map.get(sid);
      if (data) insertSessionContext(sid, data.title, data.messages);
    });
  });
}

// ── セッション詳細ビュー ──────────────────────────────────────────────────────
function renderSessionDetail(messages) {
  const list = document.getElementById('message-list');

  if (messages.length === 0) {
    list.innerHTML = '<div class="empty-state"><div class="empty-icon">◈</div><div class="empty-text">No messages in this session.</div></div>';
    return;
  }

  const title = messages.find(m => m.role === 'user')?.content.slice(0, 30) || '(no title)';
  const highlighted = (text) => currentQuery
    ? escHtml(text).replace(new RegExp(escRegex(currentQuery), 'gi'), s => '<span class="highlight">' + s + '</span>')
    : escHtml(text);

  const backBtn = '<div class="back-btn" id="drill-back">‹ Back to list</div>';
  const header  = '<div class="drill-header">' + escHtml(title) + ' <span class="sess-badge">' + messages.length + '</span></div>';

  const items = messages.map(m => {
    const timeStr = new Date(m.timestamp).toLocaleString('en', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    const preview = m.content.slice(0, 100);
    const full    = m.content;
    return '<div class="msg-item" data-id="' + m.id + '">' +
      '<div class="msg-header">' +
        '<span class="role-badge ' + m.role + '">' + (m.role === 'user' ? 'YOU' : 'AI') + '</span>' +
        '<span class="msg-time">' + timeStr + '</span>' +
        '<button class="msg-insert-btn" data-id="' + escHtml(m.id) + '">⚡ 挿入</button>' +
      '</div>' +
      '<div class="msg-preview">' + highlighted(preview) + (m.content.length > 100 ? '…' : '') + '</div>' +
      '<div class="msg-full">' + escHtml(full) + '</div>' +
    '</div>';
  }).join('');

  list.innerHTML = backBtn + header + items;

  document.getElementById('drill-back')?.addEventListener('click', () => {
    _drillSessionId = null;
    renderMessages();
  });

  list.querySelectorAll('.msg-item').forEach(el => {
    el.addEventListener('click', (e) => {
      if (e.target.classList.contains('msg-insert-btn')) return;
      el.classList.toggle('expanded');
    });
  });

  list.querySelectorAll('.msg-insert-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const id  = btn.dataset.id;
      const msg = messages.find(m => m.id === id);
      if (msg) insertMessageContext(title, msg);
    });
  });
}

// ── 挿入: セッション全体 ──────────────────────────────────────────────────────
function insertSessionContext(sid, title, messages) {
  const summary = messages
    .filter(m => m.role === 'user')
    .slice(0, 3)
    .map(m => '・' + m.content.slice(0, 80).replace(/\n/g, ' '))
    .join('\n');
  const text = '【過去会話参照: ' + (title || sid) + '】\n' +
    (summary ? '関連箇所:\n' + summary + '\n' : '') +
    (currentQuery ? '検索キーワード: ' + currentQuery + '\n' : '') +
    '\n上記の過去会話を踏まえて、';
  injectToClaudeInput(text);
}

// ── 挿入: 単一メッセージ ──────────────────────────────────────────────────────
function insertMessageContext(sessionTitle, msg) {
  const text = '【過去会話参照: ' + (sessionTitle || '') + '】\n' +
    '関連箇所: ' + msg.content.slice(0, 100).replace(/\n/g, ' ') + '\n' +
    (currentQuery ? '検索キーワード: ' + currentQuery + '\n' : '') +
    '\n上記の過去会話を踏まえて、';
  injectToClaudeInput(text);
}

// ── Claude入力欄への注入（content.js 経由） ───────────────────────────────────
function injectToClaudeInput(text) {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const claudeTab = tabs.find(t => t.url && t.url.includes('claude.ai'));
    if (claudeTab) {
      chrome.tabs.sendMessage(claudeTab.id, { type: 'ORCHESTRA_SYNTHESIZE', prompt: text }, () => {
        // chrome.windows は未許可のためタブのみフォーカス
        chrome.tabs.update(claudeTab.id, { active: true }).catch(() => {});
      });
    } else {
      // claude.aiが開いていない場合はクリップボードにコピー
      navigator.clipboard.writeText(text).then(() => {
        alert('Claude.aiが開いていません。\nテキストをクリップボードにコピーしました。');
      }).catch(() => {});
    }
  });
}

function escHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
function escRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function download(content, filename, mime) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

document.getElementById('btn-export-csv').addEventListener('click', () => {
  chrome.runtime.sendMessage({ type: 'EXPORT_CSV' }, (res) => {
    if (res?.ok) {
      const ts = new Date().toISOString().slice(0,10);
      download(res.data, 'orchestra-' + ts + '.csv', 'text/csv');
    }
  });
});

document.getElementById('btn-export-json').addEventListener('click', () => {
  chrome.runtime.sendMessage({ type: 'EXPORT_JSON' }, (res) => {
    if (res?.ok) {
      const ts = new Date().toISOString().slice(0,10);
      download(res.data, 'orchestra-' + ts + '.json', 'application/json');
    }
  });
});

document.getElementById('btn-clear').addEventListener('click', () => {
  if (confirm('Delete ALL saved messages? This cannot be undone.')) {
    chrome.runtime.sendMessage({ type: 'CLEAR_ALL' }, () => {
      allMessages = [];
      renderMessages();
      loadStats();
    });
  }
});

let searchTimer;
document.getElementById('search').addEventListener('input', (e) => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => loadMessages(e.target.value.trim()), 300);
});

document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    currentRole = tab.dataset.role;
    renderMessages();
  });
});

// サイドパネルボタン
const btnSidePanel = document.getElementById('btn-sidepanel');
if (btnSidePanel) {
  btnSidePanel.addEventListener('click', () => {
    chrome.runtime.sendMessage({ type: 'OPEN_SIDE_PANEL' });
  });
}

loadStats();
loadMessages();

// ソート変更
document.getElementById('select-sort').addEventListener('change', (e) => {
  currentSort = e.target.value;
  renderMessages();
});

// 期間変更
document.getElementById('select-period').addEventListener('change', (e) => {
  currentPeriod = e.target.value;
  renderMessages();
});

// 2秒ごとに自動更新
setInterval(() => {
  loadStats();
  loadMessages(currentQuery);
}, 2000);

// Tab navigation
document.querySelectorAll('[data-tab]').forEach(function(el) {
  el.addEventListener('click', function() {
    var tab = this.getAttribute('data-tab');
    var mainPanel = document.getElementById('main-panel');
    var settingsPanel = document.getElementById('settings-panel');
    var navMain = document.getElementById('nav-main');
    var navSettings = document.getElementById('nav-settings');
    if (mainPanel) mainPanel.classList.toggle('hidden', tab !== 'main');
    if (settingsPanel) settingsPanel.classList.toggle('active', tab === 'settings');
    if (navMain) navMain.classList.toggle('active', tab === 'main');
    if (navSettings) navSettings.classList.toggle('active', tab === 'settings');
  });
});

// ── Plan display & license management ────────────────────────────────────────

const PLAN_META = {
  free: {
    label: 'Free',
    labelClass: 'accent',
    desc: 'Save &amp; search conversations · CSV/JSON export · No time limit',
    price: '$0',
    note: 'The Free plan is fully functional — no features are locked, no nudges to upgrade.<br>Orchestra works completely out of the box, forever, at no cost.',
    badgeColor: 'rgba(232,255,71,0.3)',
    badgeBg: 'rgba(232,255,71,0.1)',
    badgeTextColor: 'var(--accent)',
  },
  pro: {
    label: 'Orchestra Pro',
    labelClass: 'accent',
    desc: '5 AI parallel Orchestration · assign roles · one click to launch',
    price: '$5/mo',
    note: 'Pro plan active. Click the 🎼 5AI Orchestra button on any Claude response to launch.',
    badgeColor: 'rgba(232,255,71,0.3)',
    badgeBg: 'rgba(232,255,71,0.1)',
    badgeTextColor: 'var(--accent)',
  },
  one: {
    label: 'Orchestra One',
    labelClass: 'gold',
    desc: 'Everything · No API key · Fully autonomous · 100% local',
    price: '$10/mo',
    note: 'One plan active. Use 🎼 5AI Orchestra (semi-auto) or ⚡ Orchestra One (fully autonomous via Playwright).',
    badgeColor: 'rgba(201,168,76,0.4)',
    badgeBg: 'rgba(201,168,76,0.15)',
    badgeTextColor: '#c9a84c',
  },
};

function renderPlanUI(plan, expiry) {
  const meta = PLAN_META[plan] || PLAN_META.free;

  const nameEl = document.getElementById('plan-name-display');
  const badgeEl = document.getElementById('plan-active-badge');
  const descEl = document.getElementById('plan-desc-display');
  const priceEl = document.getElementById('plan-price-display');
  const noteEl = document.getElementById('plan-note-display');
  const expiryEl = document.getElementById('plan-expiry-display');

  if (nameEl) {
    nameEl.innerHTML =
      `<span class="plan-row-name ${meta.labelClass}">${meta.label}</span>`;
    if (badgeEl) {
      badgeEl.style.background = meta.badgeBg;
      badgeEl.style.border = `1px solid ${meta.badgeColor}`;
      badgeEl.style.color = meta.badgeTextColor;
      nameEl.appendChild(badgeEl);
    }
  }
  if (descEl) descEl.innerHTML = meta.desc;
  if (priceEl) {
    priceEl.textContent = meta.price;
    priceEl.className = 'plan-row-price' + (plan === 'one' ? ' gold' : '');
  }
  if (noteEl) noteEl.innerHTML = meta.note;

  // 有効期限表示
  if (expiryEl) {
    if (expiry && plan !== 'free') {
      const yr = expiry.slice(0,4), mo = expiry.slice(4,6), dy = expiry.slice(6,8);
      const expDate = new Date(parseInt(yr), parseInt(mo)-1, parseInt(dy), 23, 59, 59);
      const today = new Date();
      const daysLeft = Math.ceil((expDate - today) / (1000*60*60*24));
      const dispDate = `${yr}/${mo}/${dy}`;
      if (daysLeft <= 7) {
        expiryEl.innerHTML = `<span style="color:#ff6b6b">⚠ Expires in ${daysLeft} day${daysLeft===1?'':'s'} (${dispDate})</span>`;
      } else {
        expiryEl.innerHTML = `<span style="color:#8aff8a">✓ Valid until ${dispDate} (${daysLeft} days left)</span>`;
      }
      expiryEl.style.display = 'block';
    } else {
      expiryEl.style.display = 'none';
    }
  }

  // Show/hide Remove button based on whether a license is active
  const removeBtn = document.getElementById('license-remove-btn');
  if (removeBtn) removeBtn.style.display = plan !== 'free' ? 'inline-block' : 'none';
}

function loadAndRenderPlan(retry = 3) {
  chrome.runtime.sendMessage({ type: 'GET_PLAN' }, res => {
    if (chrome.runtime.lastError || !res) {
      if (retry > 0) setTimeout(() => loadAndRenderPlan(retry - 1), 200);
      return;
    }
    if (res?.ok) renderPlanUI(res.plan, res.expiry);
  });
}

// License activation
document.getElementById('license-activate-btn')?.addEventListener('click', () => {
  const input = document.getElementById('license-key-input');
  const statusEl = document.getElementById('license-status-msg');
  const key = input?.value?.trim();

  if (!key) {
    if (statusEl) { statusEl.textContent = 'Please enter a license key.'; statusEl.className = 'license-status err'; }
    return;
  }

  chrome.runtime.sendMessage({ type: 'SET_LICENSE', key }, res => {
    if (res && res.expired) {
      if (statusEl) { statusEl.textContent = 'This key has expired. Please renew your subscription.'; statusEl.className = 'license-status err'; }
      return;
    }
    if (res?.ok) {
      renderPlanUI(res.plan, res.expiry);
      if (window.applyPlanToActionBar) window.applyPlanToActionBar(res.plan);
      if (statusEl) {
        const planName = PLAN_META[res.plan]?.label || res.plan;
        statusEl.textContent = `✓ ${planName} activated successfully!`;
        statusEl.className = 'license-status ok';
      }
      if (input) input.value = '';
    } else {
      if (statusEl) { statusEl.textContent = 'Activation failed. Please try again.'; statusEl.className = 'license-status err'; }
    }
  });
});

// License removal
document.getElementById('license-remove-btn')?.addEventListener('click', () => {
  if (!confirm('Remove license key and revert to Free plan?')) return;
  chrome.runtime.sendMessage({ type: 'REMOVE_LICENSE' }, res => {
    if (res?.ok) {
      renderPlanUI('free');
      const statusEl = document.getElementById('license-status-msg');
      if (statusEl) { statusEl.textContent = 'License removed. Now on Free plan.'; statusEl.className = 'license-status'; }
    }
  });
});

// Load plan on popup open
loadAndRenderPlan();

// ── 合議ステータス カウントアップ + 協議/協業ラベル ──────────────────────────────
window.__orchestraTimers = {};

function updateStatusBar(mode) {
  const modeLabel = mode === 'collaboration' ? '🤝 協業' : '💬 協議';
  const modeColor = mode === 'collaboration' ? '#4fc3f7' : '#e8ff47';
  let bar = document.getElementById('orchestra-status-bar');
  if (!bar) {
    bar = document.createElement('div');
    bar.id = 'orchestra-status-bar';
    bar.style.cssText = [
      'position:fixed', 'bottom:0', 'left:0', 'right:0',
      'background:#111', 'border-top:1px solid #333',
      'padding:6px 10px', 'font-size:10px', 'z-index:9999',
      'display:flex', 'flex-wrap:wrap', 'gap:6px', 'align-items:center'
    ].join(';');
    document.body.appendChild(bar);
  }
  const entries = Object.entries(window.__orchestraTimers).map(([name, data]) => {
    const elapsed = ((Date.now() - data.startTime) / 1000).toFixed(1);
    const statusText = data.done ? '✓' : `⏱ ${elapsed}s`;
    const color = data.done ? '#666' : modeColor;
    return `<span style="color:${color}">● ${name} ${statusText}</span>`;
  }).join('');
  bar.innerHTML = `<span style="color:${modeColor};font-weight:bold;margin-right:4px">${modeLabel}</span>${entries}`;
}

window.startOrchestraStatus = function(aiName, mode) {
  if (window.__orchestraTimers[aiName]?.interval) {
    clearInterval(window.__orchestraTimers[aiName].interval);
  }
  const startTime = Date.now();
  const interval = setInterval(() => updateStatusBar(mode), 100);
  window.__orchestraTimers[aiName] = { startTime, interval, done: false, mode };
  updateStatusBar(mode);
};

window.doneOrchestraStatus = function(aiName) {
  const t = window.__orchestraTimers[aiName];
  if (!t) return;
  clearInterval(t.interval);
  t.done = true;
  updateStatusBar(t.mode || 'deliberation');
  const allDone = Object.values(window.__orchestraTimers).every(x => x.done);
  if (allDone) {
    setTimeout(() => {
      const bar = document.getElementById('orchestra-status-bar');
      if (bar) bar.remove();
      window.__orchestraTimers = {};
    }, 3000);
  }
};

// background.js からの合議イベントを受信
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === 'ORCHESTRA_START') {
    window.__orchestraTimers = {};
    (msg.targets || []).forEach(ai => window.startOrchestraStatus(ai, msg.mode || 'deliberation'));
  }
  if (msg.type === 'ORCHESTRA_DONE') {
    window.doneOrchestraStatus(msg.ai);
  }
});

// ── AI Target Selector ───────────────────────────────────────────────────────
(function initTargetSelector() {
  let _bound = false; // 二重登録防止フラグ

  function restoreChecked() {
    const rows = document.querySelectorAll('.ai-target-row');
    if (!rows.length) return;
    chrome.runtime.sendMessage({ type: 'GET_TARGETS' }, (res) => {
      const saved = (res && res.targets) ? res.targets : ['ChatGPT','Gemini','Perplexity','Copilot','Genspark'];
      rows.forEach(row => {
        if (saved.includes(row.dataset.ai)) {
          row.classList.add('checked');
        } else {
          row.classList.remove('checked');
        }
      });
    });
  }

  function bindTargetRows() {
    const rows = document.querySelectorAll('.ai-target-row');
    if (!rows.length) return;

    // 保存済み選択を復元（毎回）
    restoreChecked();

    // クリックイベントは初回のみ登録（二重登録防止）
    if (_bound) return;
    _bound = true;

    rows.forEach(row => {
      row.addEventListener('click', () => {
        row.classList.toggle('checked');
        const allRows = document.querySelectorAll('.ai-target-row');
        const selected = Array.from(allRows)
          .filter(r => r.classList.contains('checked'))
          .map(r => r.dataset.ai);
        // 最低1つは必ず選択
        if (selected.length === 0) {
          row.classList.add('checked');
          return;
        }
        chrome.runtime.sendMessage({ type: 'SET_TARGETS', targets: selected });
      });
    });
  }

  // nav-tab クリック時にも復元（Settingsタブ切替後）
  document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      setTimeout(bindTargetRows, 150);
    });
  });

  // 初期実行
  bindTargetRows();
})();


// ── Action Bar: Plan-aware unlock ────────────────────────────────────────────
(function initActionBar() {
  window.applyPlanToActionBar = function(plan) {
    const isPro = plan === 'pro' || plan === 'one';
    const isOne = plan === 'one';

    // Header badge
    const badge = document.getElementById('header-plan-badge');
    if (badge) {
      badge.className = 'plan-badge';
      if (isOne) {
        badge.classList.add('one');
        badge.textContent = 'ONE';
      } else if (isPro) {
        badge.classList.add('pro');
        badge.textContent = 'PRO';
      }
    }

    // AI Share button (Pro+)
    const shareBtn = document.getElementById('action-share');
    if (shareBtn) {
      if (isPro) {
        shareBtn.classList.remove('locked');
        shareBtn.classList.add('unlocked');
        shareBtn.addEventListener('click', () => {
          chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs[0]) {
              chrome.tabs.sendMessage(tabs[0].id, { type: 'ORCHESTRA_SHARE' });
              window.close();
            }
          });
        });
      } else {
        shareBtn.classList.add('locked');
        shareBtn.addEventListener('click', () => {
          // Settingsタブへ誘導
          const navSettings = document.getElementById('nav-settings');
          if (navSettings) navSettings.click();
          const licInput = document.getElementById('license-key-input');
          if (licInput) {
            licInput.focus();
            licInput.style.borderColor = 'var(--accent)';
            setTimeout(() => { licInput.style.borderColor = ''; }, 2000);
          }
        });
      }
    }

    // AI Collab button (One only)
    const collabBtn = document.getElementById('action-collab');
    if (collabBtn) {
      if (isOne) {
        collabBtn.classList.remove('locked');
        collabBtn.classList.add('unlocked');
        collabBtn.addEventListener('click', () => {
          chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs[0]) {
              chrome.tabs.sendMessage(tabs[0].id, { type: 'ORCHESTRA_COLLAB' });
              window.close();
            }
          });
        });
      } else {
        collabBtn.classList.add('locked');
        collabBtn.addEventListener('click', () => {
          const navSettings = document.getElementById('nav-settings');
          if (navSettings) navSettings.click();
          const licInput = document.getElementById('license-key-input');
          if (licInput) {
            licInput.focus();
            licInput.style.borderColor = '#c9a84c';
            setTimeout(() => { licInput.style.borderColor = ''; }, 2000);
          }
        });
      }
    }

    // ツールチップのテキストを言語対応
    if (window.ORCHESTRA_I18N) {
      // 将来のi18n対応用フック
    }
  }

  // プランを取得してアクションバーに反映
  function fetchAndApplyPlan(retry = 3) {
    chrome.runtime.sendMessage({ type: 'GET_PLAN' }, (res) => {
      if (chrome.runtime.lastError || !res) {
        if (retry > 0) setTimeout(() => fetchAndApplyPlan(retry - 1), 200);
        return;
      }
      if (res?.ok) {
        window.applyPlanToActionBar(res.plan);
        renderPlanUI(res.plan);
      }
    });
  }
  fetchAndApplyPlan();

  // プラン変更を監視（ライセンス有効化直後に反映）
  chrome.storage.onChanged.addListener((changes) => {
    if (changes.license_plan) {
      const newPlan = changes.license_plan.newValue || 'free';
      window.applyPlanToActionBar(newPlan);
      chrome.runtime.sendMessage({ type: 'GET_PLAN' }, r => {
        renderPlanUI(newPlan, r?.expiry);
      });
    }
  });
})();
